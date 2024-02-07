from datetime import datetime, timedelta

import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    token_type: str,
    private_key: str = settings.auth_jwt.PRIVATE_KEY_PATH.read_text(),
    algorithm: str = settings.auth_jwt.ALGORITHM,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta is None:
        expire_timedelta = timedelta(minutes=15)
    expire = now + expire_timedelta

    to_encode.update(
        token_type=token_type,
        exp=expire,
        iat=now,
    )

    encoded = jwt.encode(
        to_encode,
        key=private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.PUBLIC_KEY_PATH.read_text(),
    algorithm: str = settings.auth_jwt.ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded
