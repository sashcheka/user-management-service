from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from models import User

from .tokens import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
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


async def get_current_auth_user(
    payload: dict = Depends(get_current_token_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    id: str = payload.get("sub")

    stmt = select(User).where(User.id == id)
    result = await session.execute(stmt)
    user = result.scalar()

    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid (user not found)",
    )


def get_current_active_auth_user(
    user: User = Depends(get_current_auth_user),
) -> User:
    if not user.is_blocked:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )
