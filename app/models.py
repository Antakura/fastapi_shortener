from pydantic import computed_field
from sqlmodel import Field, SQLModel

from app.config import encryptor


class UrlBase(SQLModel):
    full_url: str = Field(...)


class Url(UrlBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UrlPublic(UrlBase):
    id: int

    @computed_field
    @property
    def short_code(self) -> str:
        return encryptor.encode(self.id)

    @computed_field
    @property
    def short_url(self) -> str:
        return f"http://127.0.0.1:8000/{self.short_code}"


class UrlCreate(UrlBase):
    full_url: str
