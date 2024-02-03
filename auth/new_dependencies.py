from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import (
    InvalidTokenError,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth.tokens_utils import decode_jwt
from core.db_helper import db_helper
from models import User

security = HTTPBearer()


async def get_auth_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
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


async def get_auth_user(
    payload: dict = Depends(get_auth_user_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user: User = result.scalar()

    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
    )


def get_active_auth_user(
    user: User = Depends(get_auth_user),
) -> User:
    if not user.is_blocked:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )
