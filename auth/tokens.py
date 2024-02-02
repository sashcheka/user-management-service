from datetime import datetime, timedelta

import jwt
from fastapi import Depends, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db_helper import db_helper
from core.redis_helper import redis_client
from core.utils import validate_password
from models import User

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.refresh_token_expire_minutes


async def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    forbidden_exp = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )

    result = await session.execute(select(User).where(User.username == username))
    user = result.scalars().first()

    if not user:
        raise unauthed_exp

    if not validate_password(password=password, hashed_password=user.password):
        raise unauthed_exp

    if user.is_blocked:
        raise forbidden_exp

    return user


def verify_refresh_token(token: str):
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

    if not redis_client.exists(token):
        raise unauthed_exp
    redis_client.delete(token)

    try:
        payload = decode_jwt(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token or blacklisted",
            )

        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            raise unauthed_exp

        return payload

    except jwt.ExpiredSignatureError:
        raise unauthed_exp

    except jwt.PyJWTError as jwt_error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"JWT error: {str(jwt_error)}",
        )


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

    redis_client.setex(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


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
