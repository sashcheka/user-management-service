from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_auth_user
from core.db_helper import db_helper
from models import User
from models.role import Role

from . import crud


async def user_by_id(
    user_id: Annotated[UUID4, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user = await crud.get_user(session=session, user_id=user_id)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id: {user_id} not found",
    )


def verify_admin_or_moderator_access(
    current_user: User = Depends(get_current_auth_user),
):
    if current_user.role in (Role.ADMIN, Role.MODERATOR):
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )
