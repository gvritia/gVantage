from src.api.tinkoff_client import TinkoffSandboxClient

if __name__ == "__main__":
    client = TinkoffSandboxClient()
    client.create_account()
    client.show_info()
    client.delete_all_accounts()
