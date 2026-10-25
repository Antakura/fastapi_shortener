from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from app.config import encryptor
from app.database import SessionDep, create_tables
from app.models import Url, UrlCreate, UrlPublic

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_tables()


@app.post("/urls/", response_model=UrlPublic, status_code=status.HTTP_201_CREATED)
def create_url(url: UrlCreate, session: SessionDep):
    db_url = Url.model_validate(url)
    session.add(db_url)
    session.commit()
    session.refresh(db_url)
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
