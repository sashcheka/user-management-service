from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from users.schemas import UserCreateSchema, UserSchema

from .controllers import (
    create_user_controller,
    login_user_controller,
    refresh_token_controller,
)
from .dependencies import get_current_active_auth_user
from .schemas import UserLoginSchema
from .tokens import validate_auth_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup/")
async def signup(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await create_user_controller(session=session, user_in=user_in)


@router.post("/login/")
def login(user: UserLoginSchema = Depends(validate_auth_user)):
    return login_user_controller(user=user)


@router.post("/refresh-token/")
def refresh_token(
    _: UserSchema = Depends(get_current_active_auth_user),
    refresh_token_in: str = Body(...),
):
    return refresh_token_controller(refresh_token=refresh_token_in)
