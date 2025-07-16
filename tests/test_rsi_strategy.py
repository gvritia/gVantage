import pytest
import numpy as np
from gVantage.src.strategies.rsi import RSIStrategy


class DummyTradeClient:
    def __init__(self):
        self.buy_called = False
        self.sell_called = False

    def buy_stock(self, figi, quantity):
        self.buy_called = True

    def sell_stock(self, figi, quantity):
        self.sell_called = True


class DummySettings:
    TINKOFF_API_TOKEN_SANDBOX = "test"
    DB_URL = "sqlite://"
    RSI_PERIOD = 14
    GPT_MODEL_NAME = "gpt-4o"
    OPENAI_API_KEY = "test"


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    monkeypatch.setattr(
        "gVantage.src.api.tinkoff_market_data_client.get_settings",
        lambda: DummySettings()
    )
    monkeypatch.setattr(
        "gVantage.src.api.tinkoff_trade_client.get_settings",
        lambda: DummySettings()
    )


def test_calculate_rsi_basic():
    closes = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    strategy = RSIStrategy(figi="TEST", rsi_period=14, quantity=1)
    rsi = strategy.calculate_rsi(closes)
    assert len(rsi) == len(closes)
    assert np.all(rsi >= 0) and np.all(rsi <= 100)


def test_signal_buy(monkeypatch):
    strategy = RSIStrategy(figi="TEST", rsi_period=3, quantity=1)
    strategy.trade_client = DummyTradeClient()
    monkeypatch.setattr(strategy.market_data_client, "get_candles",
                        lambda *a, **kw: [type("C", (), {"close": x}) for x in [10, 9, 8, 7, 6, 5]])
    strategy.run()
    assert strategy.trade_client.buy_called
    assert not strategy.trade_client.sell_called


def test_signal_sell(monkeypatch):
    strategy = RSIStrategy(figi="TEST", rsi_period=3, quantity=1)
    strategy.trade_client = DummyTradeClient()
    # Данные для RSI > 70 (очень резкий рост)
    closes = [10, 100, 190, 280]  # ещё более резкий рост
    monkeypatch.setattr(strategy.market_data_client, "get_candles",
                        lambda *a, **kw: [type("C", (), {"close": x}) for x in closes])
    rsi = strategy.calculate_rsi(np.array(closes))
    print("RSI values:", rsi)
    strategy.run()
    assert strategy.trade_client.sell_called
    assert not strategy.trade_client.buy_called


def test_signal_hold(monkeypatch):
    strategy = RSIStrategy(figi="TEST", rsi_period=3, quantity=1)
    strategy.trade_client = DummyTradeClient()
    # Данные для RSI ≈ 50 (боковое движение)
    monkeypatch.setattr(strategy.market_data_client, "get_candles",
                        lambda *a, **kw: [type("C", (), {"close": x}) for x in [10, 11, 10, 11, 10, 11]])
    strategy.run()
    assert not strategy.trade_client.buy_called
    assert not strategy.trade_client.sell_called
