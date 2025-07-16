# gVantage/src/api/tinkoff_trade_client.py
import logging
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest import OrderDirection, OrderType
from gVantage.config.settings import get_settings

logger = logging.getLogger(__name__)


class TinkoffTradeClient:
    def __init__(self):
        settings = get_settings()
        self.token = settings.TINKOFF_API_TOKEN_SANDBOX
        if not self.token:
            logger.error("Токен Tinkoff API для песочницы не найден.")
            raise ValueError("API token is required for trading")

    def buy_stock(self, figi, quantity):
        with SandboxClient(self.token) as client:
            accounts = client.users.get_accounts().accounts
            if not accounts:
                logger.error("Нет sandbox-аккаунтов для торговли.")
                return None
            account_id = accounts[0].id
            response = client.orders.post_order(
                figi=figi,
                quantity=quantity,
                price=0,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                account_id=account_id,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            logger.info(f"Заявка на покупку отправлена: {response}")
            return response

    def sell_stock(self, figi, quantity):
        with SandboxClient(self.token) as client:
            accounts = client.users.get_accounts().accounts
            if not accounts:
                logger.error("Нет sandbox-аккаунтов для торговли.")
                return None
            account_id = accounts[0].id
            response = client.orders.post_order(
                figi=figi,
                quantity=quantity,
                price=0,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                account_id=account_id,
                order_type=OrderType.ORDER_TYPE_MARKET
            )
            logger.info(f"Заявка на продажу отправлена: {response}")
            return response
