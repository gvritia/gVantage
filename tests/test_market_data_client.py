import os
from gVantage.src.api.tinkoff_client import MarketDataClient
from gVantage.src.api.tinkoff_market_data_client import MarketDataClient, AsyncMarketDataClient
from tinkoff.invest.sandbox.client import SandboxClient
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval
import pytest # Добавляем pytest для более структурированных тестов
import asyncio

# Используем фикстуру, чтобы не дублировать инициализацию клиента
@pytest.fixture(scope="module")
def market_data_client():
    client = MarketDataClient()
    yield client
    # client.__exit__(None, None, None) # Можно добавить очистку, если необходимо

@pytest.fixture(scope="module")
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


def test_get_order_book():
    token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    assert token, "TINKOFF_API_TOKEN_SANDBOX не установлен в переменных окружения."
    figi = "BBG004730ZJ9"
    depth = 10

    with SandboxClient(token) as client:
        order_book = client.market_data.get_order_book(figi=figi, depth=depth)
        assert order_book is not None
        # Дополнительные проверки на структуру стакана
        assert hasattr(order_book, 'bids')
        assert hasattr(order_book, 'asks')
        print(f"\nСтакан: {order_book}")


def test_get_last_price():
    token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    assert token, "TINKOFF_API_TOKEN_SANDBOX не установлен в переменных окружения."
    figi = "BBG004730ZJ9"

    with SandboxClient(token) as client:
        response = client.market_data.get_last_prices(figi=[figi])
        assert response is not None
        assert len(response.last_prices) > 0
        print(f"\nПоследняя цена: {response.last_prices[0]}")

if __name__ == "__main__":
    print("Запуск тестов...")
    asyncio.run(test_async_get_candles(AsyncMarketDataClient())) # Придется передавать инстанс, что не очень хорошо без pytest
    test_get_candles(MarketDataClient())
    test_get_order_book()
    test_get_last_price()