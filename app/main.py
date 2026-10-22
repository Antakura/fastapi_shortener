from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, SQLModel, create_engine

from app.config import encryptor
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
    decoded = encryptor.decode(short_url)
    if not decoded:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid short url"
        )

    url_id = decoded[0]
    url = session.get(Url, url_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
        )

    return RedirectResponse(url=url.full_url, status_code=status.HTTP_302_FOUND)
