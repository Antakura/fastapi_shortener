from functools import lru_cache

from hashids import Hashids
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


encryptor = Hashids(salt=get_settings().SECRET_KEY, min_length=6)
