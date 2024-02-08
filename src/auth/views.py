from fastapi import APIRouter, Body, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from users.schemas import UserCreateSchema, UserSchema

from .controllers import (
    consume_test_message_controller,
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
from .validators import auth_user_validator

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/")
async def signup(
    user_in: UserCreateSchema = Depends(get_user_signup_data),
    image: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await create_user_controller(
        user_in=user_in,
        session=session,
        image=image,
    )


@router.post("/login/")
async def login(
    user: UserLoginSchema = Depends(auth_user_validator.validate_auth_user),
):
    return await login_user_controller(user=user)


@router.post("/refresh-token/")
def refresh_token(
    _: UserSchema = Depends(get_active_auth_user),
    refresh_token_in: RefreshTokenSchema = Body(...),
):
    return refresh_token_controller(refresh_token=refresh_token_in.refresh_token)


@router.get("/payload/")
def debug_decode_token(payload: dict = Depends(get_auth_user_payload)):
    return payload


@router.post("/reset-password/")
def reset_password(
    email_in: EmailSchema,
    _: UserSchema = Depends(get_active_auth_user),
):
    return reset_password_controller(email=email_in.email)


@router.get("/consume-message-test/")
async def consume_message_test(
    _: UserSchema = Depends(get_active_auth_user),
):
    return consume_test_message_controller()
