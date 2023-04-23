from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Any settings here will be overridden by .env file. Start the application
    with uvicorn with the option: --env-file <path_to_env_file>
    """
    PROJECT_NAME: str = "Lotto API"
    API_PREFIX: str = "/api"
    API_VERSION_PREFIX: str = "/v1"
    POSTGRES_DB_URI: str = None
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    settings = Settings()
    return Settings()
