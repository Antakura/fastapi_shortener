from sqlmodel import Field, SQLModel


class UrlBase(SQLModel):
    full_url: str = Field(...)


class Url(UrlBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class UrlPublic(UrlBase):
    id: int


class UrlCreate(UrlBase):
    full_url: str
