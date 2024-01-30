from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from users.schemas import UserCreateSchema, UserSchema
from . import crud
from .dependencies import get_current_token_payload, get_current_active_auth_user
from .schemas import UserLoginSchema
from .tokens import (
    validate_auth_user,
    create_access_token,
    create_refresh_token,
    redis_client,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    verify_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/")
async def signup(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.create_user(session=session, user_in=user_in)


@router.post("/login/")
async def login(user: UserLoginSchema = Depends(validate_auth_user)):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "password": user.password,
    }

    access_token = create_access_token(payload=payload)
    refresh_token = create_refresh_token(payload=payload)

    redis_client.setex(refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


@router.get("/users/me/")
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "user": user,
        "logged_in_at": iat,
    }


@router.post("/refresh-token/")
def refresh_token(refresh_token_in: str = Body(...)):
    payload = verify_refresh_token(refresh_token_in)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token or blacklisted",
        )
    access_token = create_access_token(payload=payload)
    new_refresh_token = create_refresh_token(payload=payload)

    redis_client.setex(new_refresh_token, REFRESH_TOKEN_EXPIRE_MINUTES * 60, "valid")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": new_refresh_token,
    }
