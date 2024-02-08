from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import get_user_by_username
from auth.schemas import UserLoginSchema
from core.db_helper import db_helper
from core.password_utils import validate_password
from models import User

unauthed_exp = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
)
forbidden_exp = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="User inactive",
)


async def validate_auth_user(
    user_in: UserLoginSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user = await get_user_by_username(session=session, user_in=user_in)
    if not user:
        raise unauthed_exp

    if not validate_password(
        password=user_in.password,
        hashed_password=user.password,
    ):
        raise unauthed_exp

    if user.is_blocked:
        raise forbidden_exp

    return user
