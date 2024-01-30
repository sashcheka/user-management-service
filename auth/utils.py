from datetime import datetime, timedelta

import bcrypt
import jwt
import redis
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import UUID4

from core.config import settings

from .temp_models import UserCreate, UserLogin, UserSignup

ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.refresh_token_expire_minutes


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
redis_client = redis.Redis(host="redis", port=6379, db=0)


fake_users_db: dict[UUID4, UserCreate] = {}


def validate_auth_user(
    username: str = Form(),
    password: str = Form(),
):
    unauthed_exp = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    forbidden_exp = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )

    if not (user := fake_users_db.get(username)):
        raise unauthed_exp

    if not validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exp

    if not user.active:
        raise forbidden_exp
    return user


def verify_refresh_token(token: str):
    if not redis_client.exists(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    redis_client.delete(token)

    try:
        payload = decode_jwt(token)
        if payload.get("exp") < datetime.utcnow().timestamp():
            return {}
        return payload
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> UserLogin:
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
) -> UserCreate:
    user_id: UUID4 = payload.get("sub")
    if user := fake_users_db.get(user_id):
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid (user not found)",
    )


def get_current_active_auth_user(
    user: UserSignup = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
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


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pdw_bytes: bytes = password.encode()
    return bcrypt.hashpw(password=pdw_bytes, salt=salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )
