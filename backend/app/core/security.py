import os
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("JWT_SECRET", "change_me")
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def _normalize_password(password: str) -> bytes:
    if password is None:
        password = ""
    # bcrypt limite à 72 bytes ⇒ tronquer
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_normalize_password(password), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_normalize_password(password), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_token(str(user_id), timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access")


def create_refresh_token(user_id: int) -> str:
    return create_token(str(user_id), timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh")
