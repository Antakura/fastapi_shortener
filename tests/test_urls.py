import pytest
from fastapi import status
from pydantic import ValidationError
from sqlmodel import Session, select

from app.config import encryptor
from app.models import Url, UrlCreate, UrlPublic

VALID_URL = "https://example.com/some/very/long/path?query=1"
ANOTHER_URL = "https://other.example.com/page"
INVALID_SHORT_CODE = "!!!"


class TestCreateUrl:
    def test_returns_201_with_url_public(self, client):
        response = client.post("/urls/", json={"full_url": VALID_URL})

        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["full_url"] == VALID_URL
        assert isinstance(body["id"], int)
        assert body["short_code"] == encryptor.encode(body["id"])
        assert body["short_url"] == f"http://127.0.0.1:8000/{body['short_code']}"

    def test_url_is_persisted(self, client, db_engine):
        client.post("/urls/", json={"full_url": VALID_URL})

        with Session(db_engine) as session:
            urls = session.exec(select(Url)).all()

        assert [url.full_url for url in urls] == [VALID_URL]

    def test_missing_full_url_returns_422(self, client):
        response = client.post("/urls/", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_urls_get_unique_ids_and_short_codes(self, client):
        first = client.post("/urls/", json={"full_url": VALID_URL}).json()
        second = client.post("/urls/", json={"full_url": ANOTHER_URL}).json()

        assert first["id"] != second["id"]
        assert first["short_code"] != second["short_code"]


class TestFetchUrl:
    def test_redirects_to_original_url(self, client):
        created = client.post("/urls/", json={"full_url": VALID_URL}).json()

        response = client.get(f"/url/{created['short_code']}", follow_redirects=False)

        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == VALID_URL

    def test_invalid_short_code_returns_404(self, client):
        response = client.get(f"/url/{INVALID_SHORT_CODE}", follow_redirects=False)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Invalid short url"

    def test_unknown_url_returns_404(self, client):
        code = encryptor.encode(999_999)

        response = client.get(f"/url/{code}", follow_redirects=False)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "URL not found"


class TestModels:
    def test_url_public_short_code(self):
        public = UrlPublic(id=42, full_url=VALID_URL)

        assert public.short_code == encryptor.encode(42)

    def test_url_public_short_url(self):
        public = UrlPublic(id=42, full_url=VALID_URL)

        assert public.short_url == f"http://127.0.0.1:8000/{encryptor.encode(42)}"

    def test_url_create_requires_full_url(self):
        with pytest.raises(ValidationError):
            UrlCreate()
