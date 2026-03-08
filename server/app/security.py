from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

password_hash = PasswordHash.recommended()


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=get_settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expire}

    return jwt.encode(
        payload=payload,
        key=get_settings().JWT_SECRET_KEY,
        algorithm=get_settings().JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    data = jwt.decode(
        jwt=token,
        key=get_settings().JWT_SECRET_KEY,
        algorithms=[get_settings().JWT_ALGORITHM],
    )

    sub: str | None = data.get("sub")
    if sub is None:
        raise jwt.InvalidTokenError("Missing subject in token")

    return sub
