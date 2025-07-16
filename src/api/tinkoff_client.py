# gVantage/src/api/tinkoff_client.py
import logging
# from tinkoff.invest import Client # Будет использоваться для реального API

logger = logging.getLogger(__name__)

# Этот файл предназначен для будущего клиента реальной торговли.
# Пока что здесь нет функциональности.
# В будущем здесь будут классы типа TinkoffRealAccountClient, TinkoffRealTradeClient и т.д.

# Пример заглушки, если нужно, чтобы он не был совсем пустым:
class TinkoffRealAccountClient:
    def __init__(self):
        logger.info("TinkoffRealAccountClient: Инициализация для реальной торговли (пока не реализовано).")
        # settings = get_settings()
        # self.token = settings.TINKOFF_API_TOKEN_REAL # Будет использоваться реальный токен
        # self.client = Client(self.token)

    def get_accounts(self):
        logger.info("TinkoffRealAccountClient: Получение аккаунтов (пока не реализовано).")
        return []