import os
# from tinkoff.invest import Client
# from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX
from dotenv import load_dotenv
from tinkoff.invest.sandbox.client import SandboxClient
# from tinkoff.invest import exceptions
# from tinkoff.invest import AccountType

load_dotenv()


def get_token():
    try:
        global token
        token = os.getenv("TINKOFF_API_TOKEN_SANDBOX")
    except ValueError:
        return None


def create_sandbox_account():
    if token:
        try:
            with SandboxClient(token) as client:
                response = client.sandbox.open_sandbox_account()
                print(f"✅ Создан аккаунт: {response.account_id}")
                return response.account_id
        except Exception as e:
            print(f"❌ Ошибка при создании аккаунта: {e}")
    else:
        print(f"❌ Ошибка при создании аккаунта! Проверьте корректность токена")


def delete_all_sandbox_accounts():
    if token:
        try:
            with SandboxClient(token) as client:
                accounts = client.users.get_accounts().accounts
                print(f"🔍 Найдено sandbox-аккаунтов: {len(accounts)}")
                for acc in accounts:
                    client.sandbox.close_sandbox_account(account_id=acc.id)
                    print(f"🗑 Закрыт аккаунт: {acc.id}")
        except Exception as e:
            print(f"❌ Ошибка при удалении аккаунтов: {e}")
    else:
        print(f"❌ Ошибка при удалении аккаунтов! Проверьте корректность токена")

def show_info():
    if token != None:
        try:
            with SandboxClient(token) as client:
                user = client.users.get_accounts()
                information = client.users.get_info()
                print(user)
                print(information)
        except Exception as e:
            print(e)
    else:
        print(f"❌ Ошибка при удалении аккаунтов! Проверьте корректность токена")

if __name__ == "__main__":
    get_token()
    account_id = create_sandbox_account()
    show_info()
    delete_all_sandbox_accounts()
