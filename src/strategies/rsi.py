import logging
import numpy as np
from datetime import datetime, timedelta
from tinkoff.invest import CandleInterval
from gVantage.src.api.tinkoff_market_data_client import MarketDataClient
from gVantage.src.api.tinkoff_trade_client import TinkoffTradeClient
from gVantage.config.settings import get_settings

logger = logging.getLogger(__name__)


class RSIStrategy:
    def __init__(self, figi, rsi_period=14, quantity=1):
        self.figi = figi
        self.rsi_period = rsi_period
        self.quantity = quantity
        self.market_data_client = MarketDataClient()
        self.trade_client = TinkoffTradeClient()

    def calculate_rsi(self, closes):
        deltas = np.diff(closes)
        seed = deltas[:self.rsi_period]
        up = seed[seed > 0].sum() / self.rsi_period
        down = -seed[seed < 0].sum() / self.rsi_period
        if down == 0:
            rs = np.inf
        else:
            rs = up / down
        rsi = np.zeros_like(closes)
        rsi[:self.rsi_period] = 100. - 100. / (1. + rs)

        for i in range(self.rsi_period, len(closes)):
            delta = deltas[i - 1]
            upval = max(delta, 0)
            downval = -min(delta, 0)
            up = (up * (self.rsi_period - 1) + upval) / self.rsi_period
            down = (down * (self.rsi_period - 1) + downval) / self.rsi_period
            if down == 0:
                rs = np.inf
            else:
                rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
        return rsi

    def run(self):
        to = datetime.utcnow()
        from_ = to - timedelta(minutes=self.rsi_period * 3)
        candles = self.market_data_client.get_candles(
            self.figi, from_, to, CandleInterval.CANDLE_INTERVAL_1_MIN
        )
        if not candles or len(candles) < self.rsi_period + 1:
            logger.warning("Недостаточно данных для расчёта RSI.")
            return

        closes = np.array([c.close for c in candles])
        rsi = self.calculate_rsi(closes)
        last_rsi = rsi[-1]
        logger.info(f"Последний RSI: {last_rsi:.2f}")

        if last_rsi < 30:
            logger.info("Сигнал на покупку (RSI < 30)")
            self.trade_client.buy_stock(self.figi, self.quantity)
        elif last_rsi > 70:
            logger.info("Сигнал на продажу (RSI > 70)")
            self.trade_client.sell_stock(self.figi, self.quantity)
        else:
            logger.info("Нет сигнала для сделки.")

# Пример запуска стратегии:
# strategy = RSIStrategy(figi="BBG004730ZJ9", rsi_period=14, quantity=1)
# strategy.run()
