# gVantage/src/api/tinkoff_market_data_client.py
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest import AsyncClient
import logging
from gVantage.config.settings import get_settings

logger = logging.getLogger(__name__)


class MarketDataClient:
    def __init__(self):
        settings = get_settings()
        self.token = settings.TINKOFF_API_TOKEN_SANDBOX
        if not self.token:
            logger.error("Токен Tinkoff API для песочницы не найден при инициализации MarketDataClient.")
            raise ValueError("API token is required for MarketDataClient")
        self.client = SandboxClient(self.token)

    def get_candles(self, figi, from_, to, interval):
        try:
            return self.client.market_data.get_candles(
                figi=figi,
                from_=from_,
                to=to,
                interval=interval
            ).candles
        except Exception as e:
            logger.exception(f"Ошибка при получении свечей для FIGI {figi}: {e}")
            return []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.__exit__(exc_type, exc_val, exc_tb)


class AsyncMarketDataClient:
    def __init__(self):
        settings = get_settings()
        self.token = settings.TINKOFF_API_TOKEN_SANDBOX
        if not self.token:
            logger.error("Токен Tinkoff API для песочницы не найден при инициализации AsyncMarketDataClient.")
            raise ValueError("API token is required for AsyncMarketDataClient")

    async def get_candles(self, figi, from_, to, interval):
        try:
            async with AsyncClient(self.token) as client:
                return (await client.market_data.get_candles(
                    figi=figi,
                    from_=from_,
                    to=to,
                    interval=interval
                )).candles
        except Exception as e:
            logger.exception(f"Ошибка при асинхронном получении свечей для FIGI {figi}: {e}")
            return []