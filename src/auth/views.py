import logging

from fastapi import APIRouter, Body, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from users.schemas import UserCreateSchema, UserSchema

from .controllers import (
    consume_message_controller,
    create_user_controller,
    login_user_controller,
    refresh_token_controller,
    reset_password_controller,
)
from .dependencies import (
    get_active_auth_user,
    get_auth_user_payload,
    get_user_signup_data,
)
from .schemas import EmailSchema, RefreshTokenSchema, UserLoginSchema
from .validators import validate_auth_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/")
async def signup(
    user_in: UserCreateSchema = Depends(get_user_signup_data),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    logging.info(f"Signup endpoint called with user: {user_in.username}")
    return await create_user_controller(
        user_in=user_in,
        session=session,
        image=image,
    )


@router.post("/login/")
def login(
    user: UserLoginSchema = Depends(validate_auth_user),
):
    logging.info(f"Login endpoint called for user: {user.username}")
    return login_user_controller(user=user)


@router.post("/refresh-token/")
def refresh_token(
    _: UserSchema = Depends(get_active_auth_user),
    refresh_token_in: RefreshTokenSchema = Body(...),
):
    logging.info(f"Refresh token endpoint called for user: {_.username}.")
    return refresh_token_controller(refresh_token=refresh_token_in.refresh_token)


@router.get("/payload/")
def debug_decode_token(payload: dict = Depends(get_auth_user_payload)):
    return payload


@router.post("/reset-password/")
def reset_password(
    email_in: EmailSchema,
    _: UserSchema = Depends(get_active_auth_user),
):
    logging.info(f"Reset password endpoint called for user: {_.username}.")
    return reset_password_controller(email=email_in.email)


@router.get("/consume-message/")
async def consume_message(
    _: UserSchema = Depends(get_active_auth_user),
):
    return consume_message_controller()
