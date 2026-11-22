
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")

password_hash = PasswordHash.recommended()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key or secret_key == "replace_with_a_secure_random_secret":
        raise RuntimeError(
            "SECRET_KEY is missing or invalid. Check your .env file."
        )

    return secret_key


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    user_id: int,
    expires_delta: timedelta | None = None,
) -> str:
    expiration = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        get_secret_key(),
        algorithms=[ALGORITHM],
    )
