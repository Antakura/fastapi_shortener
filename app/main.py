from fastapi import FastAPI, status, Depends, HTTPException
from fastapi.responses import RedirectResponse
from hashids import Hashids
from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated

from app.config import get_settings
from app.models import Url, UrlCreate, UrlPublic

app = FastAPI()

sqlite_file_name = "db.sqlite3"
engine = create_engine(f"sqlite:///{sqlite_file_name}")


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

encryptor = Hashids(salt=get_settings().SECRET_KEY, min_length=6)


def encrypt_urls_id(long_url_id: int) -> str:
    return encryptor.encode(long_url_id)


def decrypt_hashed_url(hashed_url: str) -> int:
    return encryptor.decode(hashed_url)


@app.on_event("startup")
def on_startup():
    create_tables()


@app.post("/urls/", response_model=UrlPublic)
def create_url(url: UrlCreate, session: SessionDep):
    db_url = Url.model_validate(url)
    session.add(db_url)
    session.commit()
    session.refresh(db_url)
    # TODO: add returning encrypted url
    return db_url


@app.get("/url/{short_url}", response_model=UrlPublic)
def fetch_ful_url(short_url: str, session: SessionDep):
    decrypted_id = decrypt_hashed_url(short_url)
    url = session.get(Url, decrypted_id)
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return RedirectResponse(
        url=url.full_url, status_code=status.HTTP_302_FOUND
    )
