from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
)


password_hasher = PasswordHash.recommended()


def hash_password(password):
    return password_hasher.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id):
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )