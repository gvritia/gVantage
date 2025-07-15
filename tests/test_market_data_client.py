import os
from gVantage.src.api.tinkoff_client import MarketDataClient
from tinkoff.invest.sandbox.client import SandboxClient
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval


def test_get_candles():
    token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    client = MarketDataClient(token)
    figi = "BBG004730ZJ9"  # пример FIGI (Сбербанк)
    to = datetime.utcnow()
    from_ = to - timedelta(days=1)
    interval = CandleInterval.CANDLE_INTERVAL_1_MIN  # интервал 1 минута

    candles = client.get_candles(figi, from_, to, interval)
    assert candles is not None
    assert isinstance(candles, list)
    print(f"Получено свечей: {len(candles)}")
    print(f"Первая свеча: {candles[0]}") if candles else print("Нет свечей")


def test_get_order_book():
    token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    figi = "BBG004730ZJ9"
    depth = 10

    with SandboxClient(token) as client:
        order_book = client.market_data.get_order_book(figi=figi, depth=depth)
        assert order_book is not None
        print(f"Стакан: {order_book}")


def test_get_last_price():
    token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    figi = "BBG004730ZJ9"

    with SandboxClient(token) as client:
        response = client.market_data.get_last_prices(figi=[figi])
        assert response is not None
        assert len(response.last_prices) > 0
        print(f"Последняя цена: {response.last_prices[0]}")


if __name__ == "__main__":
    test_get_candles()
    test_get_order_book()
    test_get_last_price()
