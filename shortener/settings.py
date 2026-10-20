from hashids import Hashids
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="UTF-8")


settings = Settings()


encryptor = Hashids(salt=Settings.secret_key, min_length=6)


def encrypt_urls_id(long_url: str) -> str:
    return encryptor.encode(long_url)


def decrypt_hashed_url(hashed_url: str) -> str:
    return encryptor.decode(hashed_url)
