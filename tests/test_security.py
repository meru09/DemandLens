
from datetime import timedelta

import jwt
import pytest

from backend.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_is_hashed():
    password = "TestPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_correct_password_is_verified():
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_wrong_password_is_rejected():
    hashed = hash_password("TestPassword123!")

    assert verify_password("WrongPassword123!", hashed) is False


def test_access_token_contains_user_id():
    token = create_access_token(user_id=12)

    payload = decode_access_token(token)

    assert payload["sub"] == "12"


def test_expired_token_is_rejected():
    token = create_access_token(
        user_id=12,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_token_is_rejected():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("invalid.token.value")
