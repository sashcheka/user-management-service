from datetime import datetime, timedelta

import jwt
import redis
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from core.config import settings

from . import utils

PRIVATE_KEY = settings.auth_jwt.private_key_path.read_text()
PUBLIC_KEY = settings.auth_jwt.public_key_path.read_text()
ALGORITHM = "RS512"
ACCESS_TOKEN_EXPIRE_MINUTES = 3
REFRESH_TOKEN_EXPIRE_MINUTES = 15

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")
redis_client = redis.Redis(host="redis", port=6379, db=0)


class UserSignup(BaseModel):
    username: str
    password: str
    email: str | None = None
    active: bool = True


class UserLogin(BaseModel):
    username: str
    password: bytes
    email: str | None = None
    active: bool = True


class Token(BaseModel):
    access_token: str
    refresh_token: str


fake_users_db: dict[str, UserLogin] = {}


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

    if not utils.validate_password(
        password=password,
        hashed_password=user.password,
    ):
        raise unauthed_exp

    if not user.active:
        raise forbidden_exp
    return user


def fake_hash_password(password: str):
    return "hashed" + password


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)

    redis_client.setex(
        encoded_jwt, expire.timestamp() - datetime.utcnow().timestamp(), "valid"
    )

    return encoded_jwt


def authenticate_user(username: str, password: str):
    if username in fake_users_db and fake_users_db.get(
        username
    ).password == utils.hash_password(password):
        return fake_users_db.get(username)
    return False


def verify_refresh_token(token: str):
    if not redis_client.exists(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    redis_client.delete(token)

    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") < datetime.utcnow().timestamp():
            return {}
        return {"username": payload.get("sub")}
    except jwt.ExpiredSignatureError:
        return {}
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> UserLogin:
    try:
        payload = utils.decode_jwt(
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
) -> UserLogin:
    username: str | None = payload.get("sub")
    if user := fake_users_db.get(username):
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


@router.post("/signup/")
def signup(user: UserSignup):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already registered")

    user.password = utils.hash_password(user.password)

    fake_users_db[user.username] = UserLogin(
        username=user.username, password=user.password
    )
    return {"user": user, "message": f"User {user.username} created successfully."}


@router.post("/login/", response_model=Token)
def auth_user_issue_jwt(user: UserLogin = Depends(validate_auth_user)):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }

    access_token = utils.encode_jwt(
        jwt_payload, expire_timedelta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = utils.encode_jwt(
        jwt_payload, expire_timedelta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    redis_client.setex(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


@router.post("/refresh-token/", response_model=Token)
def refresh_token(refresh_token: str = Body(...)):
    user_dict = verify_refresh_token(refresh_token)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token or blacklisted",
        )
    access_token = utils.encode_jwt(
        user_dict, expire_timedelta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = utils.encode_jwt(
        user_dict, expire_timedelta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    # Store the new refresh token in Redis
    redis_client.setex(new_refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {"access_token": access_token, "refresh_token": new_refresh_token}


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserLogin = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "logged_in_at": iat,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
