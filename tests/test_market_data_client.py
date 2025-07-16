# gVantage/tests/test_market_data_client.py
import os
from gVantage.src.api.tinkoff_market_data_client import MarketDataClient, AsyncMarketDataClient
from tinkoff.invest.sandbox.client import SandboxClient
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval
import pytest
import asyncio
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import sys # Import sys


# === Измененные части ===

class DummySettings(BaseSettings):
    """Вспомогательный класс для мокирования настроек в тестах."""
    TINKOFF_API_TOKEN_SANDBOX: str = "test_sandbox_token"
    DB_URL: str = "sqlite:///:memory:"
    RSI_PERIOD: int = 14
    GPT_MODEL_NAME: str = "gpt-4o"
    OPENAI_API_KEY: str = "test_openai_key"

    model_config = SettingsConfigDict(
        env_file=None,
        extra='ignore'
    )

@pytest.fixture(scope="function", autouse=True)
def patch_settings(monkeypatch):
    """
    Фикстура для подмены класса Settings и функции get_settings()
    для предотвращения загрузки из .env в тестах.
    """
    # 0. Агрессивно удаляем модуль настроек из sys.modules
    # Это заставит его перезагрузиться, когда он будет импортирован в следующий раз,
    # гарантируя, что наши патчи будут применены к "свежему" модулю.
    module_name = "gVantage.config.settings"
    if module_name in sys.modules:
        del sys.modules[module_name]

    # Теперь, когда модуль будет загружен, он увидит наши патчи
    # Мы должны выполнить импорт *после* удаления из sys.modules
    # чтобы get_settings и Settings из этого модуля были "обновлены"
    from gVantage.config.settings import get_settings, Settings as RealSettings

    # 1. Очищаем кеш get_settings на случай, если она была вызвана до патча (после перезагрузки)
    get_settings.cache_clear()

    # 2. НЕПОСРЕДСТВЕННО ЗАМЕНЯЕМ КЛАСС Settings на DummySettings
    monkeypatch.setattr(f"{module_name}.Settings", DummySettings)

    # 3. Патчим функцию get_settings, чтобы она возвращала экземпляр нашего DummySettings.
    monkeypatch.setattr(f"{module_name}.get_settings", lambda: DummySettings())

    # 4. Патчим get_settings в других модулях, которые могли бы ее импортировать напрямую
    # Это избыточно, если модуль настроек был перезагружен, но безопасно.
    monkeypatch.setattr(
        "gVantage.src.api.tinkoff_market_data_client.get_settings",
        lambda: DummySettings()
    )
    monkeypatch.setattr(
        "gVantage.src.api.tinkoff_trade_client.get_settings",
        lambda: DummySettings()
    )
    monkeypatch.setattr(
        "gVantage.src.api.tinkoff_sandbox_client.get_settings",
        lambda: DummySettings()
    )
    monkeypatch.setattr(
        "gVantage.src.strategies.rsi.get_settings",
        lambda: DummySettings()
    )

    # 5. Сохраняем моки os.getenv и Path.exists как защитную меру
    def mock_getenv(name, default=None):
        if name == "TINKOFF_API_TOKEN_SANDBOX":
            return "test_sandbox_token"
        if name == "OPENAI_API_KEY":
            return "test_openai_key"
        return default

    monkeypatch.setattr(os, "getenv", mock_getenv)

    original_path_exists = Path.exists
    def mock_path_exists(self):
        if self.name == ".env":
            return False
        return original_path_exists(self)
    monkeypatch.setattr(Path, "exists", mock_path_exists)

# === Конец измененных частей ===


@pytest.fixture(scope="function")
def market_data_client():
    client = MarketDataClient()
    yield client
    # client.__exit__(None, None, None) # Можно добавить очистку, если необходимо

@pytest.fixture(scope="function")
def async_market_data_client():
    client = AsyncMarketDataClient()
    yield client

def test_get_candles(market_data_client):
    figi = "BBG004730ZJ9"  # пример FIGI (Сбербанк)
    to = datetime.utcnow()
    from_ = to - timedelta(days=1)
    interval = CandleInterval.CANDLE_INTERVAL_1_MIN  # интервал 1 минута

    candles = market_data_client.get_candles(figi, from_, to, interval)
    assert candles is not None
    assert isinstance(candles, list)
    print(f"\nПолучено свечей: {len(candles)}")
    if candles:
        print(f"Первая свеча: {candles[0]}")
    else:
        print("Нет свечей")


@pytest.mark.asyncio
async def test_async_get_candles(async_market_data_client):
    figi = "BBG004730ZJ9"
    to = datetime.utcnow()
    from_ = to - timedelta(days=1)
    interval = CandleInterval.CANDLE_INTERVAL_1_MIN

    candles = await async_market_data_client.get_candles(figi, from_, to, interval)
    assert candles is not None
    assert isinstance(candles, list)
    print(f"\nПолучено асинхронных свечей: {len(candles)}")
    if candles:
        print(f"Первая асинхронная свеча: {candles[0]}")
    else:
        print("Нет асинхронных свечей")


def test_get_order_book(market_data_client, monkeypatch):
    figi = "BBG004730ZJ9"
    depth = 10

    with SandboxClient(os.getenv("TINKOFF_API_TOKEN_SANDBOX")) as client:
        order_book = client.market_data.get_order_book(figi=figi, depth=depth)
        assert order_book is not None
        assert hasattr(order_book, 'bids')
        assert hasattr(order_book, 'asks')
        print(f"\nСтакан: {order_book}")


def test_get_last_price(market_data_client, monkeypatch):
    figi = "BBG004730ZJ9"

    # Используем SandboxClient, чтобы получить последнюю цену
    # Здесь предполагается, что токен хранится в переменной окружения TINKOFF_API_TOKEN_SANDBOX

    with SandboxClient(os.getenv("TINKOFF_API_TOKEN_SANDBOX")) as client:
        response = client.market_data.get_last_prices(figi=[figi])
        assert response is not None
        assert hasattr(response, 'last_prices')
        assert len(response.last_prices) > 0
        print(f"\nПоследняя цена: {response.last_prices[0]}")