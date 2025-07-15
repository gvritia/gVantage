import os
# from tinkoff.invest import Client
# from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX
from dotenv import load_dotenv
from tinkoff.invest.sandbox.client import SandboxClient
import logging
from tinkoff.invest import AsyncClient
# from tinkoff.invest import exceptions
# from tinkoff.invest import AccountType


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("sandbox.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Загрузка .env
load_dotenv()


class TinkoffSandboxClient:
    def __init__(self, token_env_name="TINKOFF_API_TOKEN_SANDBOX"):
        token = os.getenv(token_env_name)
        if not token:
            logger.error(f"Токен не найден. Проверь файл .env и переменную {token_env_name}")
            self.token = None
        else:
            self.token = token
            logger.info("Токен успешно загружен")

    def create_account(self):
        if not self.token:
            logger.warning("Невозможно создать аккаунт без токена")
            return None
        try:
            with SandboxClient(self.token) as client:
                response = client.sandbox.open_sandbox_account()
                logger.info(f"Создан sandbox-аккаунт: {response.account_id}")
                return response.account_id
        except Exception as e:
            logger.exception(f"Ошибка при создании sandbox-аккаунта: {e}")

    def delete_all_accounts(self):
        if not self.token:
            logger.warning("Невозможно удалить аккаунты без токена")
            return
        try:
            with SandboxClient(self.token) as client:
                accounts = client.users.get_accounts().accounts
                logger.info(f"Найдено sandbox-аккаунтов: {len(accounts)}")
                for acc in accounts:
                    client.sandbox.close_sandbox_account(account_id=acc.id)
                    logger.info(f"Закрыт аккаунт: {acc.id}")
        except Exception as e:
            logger.exception(f"Ошибка при удалении аккаунтов: {e}")

    def show_info(self):
        if not self.token:
            logger.warning("Невозможно получить информацию без токена")
            return
        try:
            with SandboxClient(self.token) as client:
                user = client.users.get_accounts()
                info = client.users.get_info()
                logger.info(f"Список аккаунтов: {user}")
                logger.info(f"Информация о пользователе: {info}")
        except Exception as e:
            logger.exception(f"Ошибка при получении информации: {e}")


class MarketDataClient:
    def __init__(self, token):
        self.token = token
        self.client = SandboxClient(self.token)  # Инициализация клиента здесь

    def get_candles(self, figi, from_, to, interval):
        # with SandboxClient(self.token) as client: # Удалить эту строку
        return self.client.market_data.get_candles(  # Использовать self.client
            figi=figi,
            from_=from_,
            to=to,
            interval=interval
        ).candles

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)


class AsyncMarketDataClient:
    def __init__(self, token):
        self.token = token

    async def get_candles(self, figi, from_, to, interval):
        async with AsyncClient(self.token) as client:
            return (await client.market_data.get_candles(
                figi=figi,
                from_=from_,
                to=to,
                interval=interval
            )).candles
