from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    TINKOFF_API_TOKEN_SANDBOX: str
    DB_URL: str = "sqlite:///./sql_app.db"
    RSI_PERIOD: int = 14
    GPT_MODEL_NAME: str = "gpt-4o"
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

@lru_cache
def get_settings():
    return Settings()