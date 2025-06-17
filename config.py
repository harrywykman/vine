from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "App Name"
    database_type: str
    database_user: str
    database_password: str
    database_host: str = "localhost"
    database_port: str = "5432"
    database_name: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


SETTINGS = get_settings()
