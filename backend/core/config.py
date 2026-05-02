from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "intelligent-rec-rag"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./dev.db"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()