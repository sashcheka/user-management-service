from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserLoginSchema
from core.db_helper import db_helper
from core.password_utils import validate_password
from models import User


class AuthUserValidator:
    def __init__(self):
        self.unauthed_exp = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
        self.forbidden_exp = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive",
        )

    async def validate_auth_user(
        self,
        user_in: UserLoginSchema,
        session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    ) -> User:
        result = await session.execute(
            select(User).where(User.username == user_in.username)
        )
        user = result.scalar()

        if not user:
            raise self.unauthed_exp

        if not validate_password(
            password=user_in.password,
            hashed_password=user.password,
        ):
            raise self.unauthed_exp

        if user.is_blocked:
            raise self.forbidden_exp

        return user


auth_user_validator = AuthUserValidator()
