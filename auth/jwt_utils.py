from datetime import datetime
from datetime import timedelta

import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    token_type: str,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
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
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
):
    decoded = jwt.decode(
        jwt=token,
        key=public_key,
        algorithms=[algorithm],
    )
    return decoded
