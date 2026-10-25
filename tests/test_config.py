from app.config import get_settings

def test_secret_key():
    assert get_settings().SECRET_KEY is not None