from tinkoff.invest.sandbox.client import SandboxClient
import logging
from gVantage.config.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("sandbox.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class TinkoffSandboxClient:
    def __init__(self):
        settings = get_settings()
        self.token = settings.TINKOFF_API_TOKEN_SANDBOX
        if not self.token:
            logger.error(
                "Токен Tinkoff API для песочницы не найден. Проверьте переменную TINKOFF_API_TOKEN_SANDBOX в .env")
        else:
            logger.info("Токен Tinkoff API для песочницы успешно загружен.")

    def create_account(self):
        if not self.token:
            logger.warning("Невозможно создать аккаунт без токена.")
            return None
        try:
            with SandboxClient(self.token) as client:
                response = client.sandbox.open_sandbox_account()
                logger.info(f"Создан sandbox-аккаунт: {response.account_id}")
                return response.account_id
        except Exception as e:
            logger.exception(f"Ошибка при создании sandbox-аккаунта: {e}")
            return None

    def delete_all_accounts(self):
        if not self.token:
            logger.warning("Невозможно удалить аккаунты без токена.")
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
            logger.warning("Невозможно получить информацию без токена.")
            return
        try:
            with SandboxClient(self.token) as client:
                user_accounts = client.users.get_accounts()
                user_info = client.users.get_info()
                logger.info(f"Список аккаунтов: {user_accounts}")
                logger.info(f"Информация о пользователе: {user_info}")
        except Exception as e:
            logger.exception(f"Ошибка при получении информации: {e}")
