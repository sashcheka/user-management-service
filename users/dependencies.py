from typing import Annotated

from fastapi import (
    HTTPException,
    status,
    Path,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper
from . import crud
from models.user import User


async def user_by_id(
    user_id: Annotated[str, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user = await crud.get_user(session=session, user_id=user_id)

    if user is not None:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found")
