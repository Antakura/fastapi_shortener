import pytest
from pydantic import ValidationError

from app.config import Settings, encryptor, get_settings


def test_secret_key():
    assert get_settings().SECRET_KEY is not None


def test_settings_are_cached():
    assert get_settings() is get_settings()


def test_settings_without_secret_key_raise_validation_error(monkeypatch, tmp_path):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValidationError):
        Settings()


def test_encryptor_roundtrip():
    for value in (1, 42, 999_999):
        assert encryptor.decode(encryptor.encode(value)) == (value,)


def test_encryptor_encode_respects_min_length():
    for value in range(1, 50):
        assert len(encryptor.encode(value)) >= 6


def test_encryptor_encode_is_deterministic():
    assert encryptor.encode(42) == encryptor.encode(42)


def test_encryptor_produces_unique_codes_for_different_ids():
    assert encryptor.encode(1) != encryptor.encode(2)


def test_encryptor_decode_invalid_returns_empty():
    assert encryptor.decode("") == ()
    # Symbols outside Base62 guaranteed won't be decoded.
    assert encryptor.decode("!!!") == ()
