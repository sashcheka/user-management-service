from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status

from auth.jwt_utils import decode_jwt, encode_jwt
from core.config import settings
from core.redis_helper import delete_token_from_redis, token_exists_in_redis

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.REFRESH_TOKEN_EXPIRE_MINUTES


def raise_unauthorized_error(detail: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
    )


def get_payload_by_token(token: str) -> dict:
    try:
        payload = decode_jwt(token)
        if not payload or payload.get("exp", 0) < datetime.utcnow().timestamp():
            raise_unauthorized_error("Invalid refresh token or expired")
        return payload

    except jwt.ExpiredSignatureError:
        raise_unauthorized_error("Invalid refresh token")

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"JWT error.",
        )


def verify_refresh_token_and_get_payload(token: str) -> dict:
    if not token_exists_in_redis(token):
        raise_unauthorized_error("Invalid refresh token")
    delete_token_from_redis(token)
    payload = get_payload_by_token(token)
    return payload


def create_access_token(payload: dict):
    return encode_jwt(
        payload=payload,
        token_type="access_token",
        expire_timedelta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(payload: dict):
    return encode_jwt(
        payload=payload,
        token_type="refresh_token",
        expire_timedelta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def generate_tokens(payload):
    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(payload=payload)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }
