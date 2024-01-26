from typing import Annotated

from fastapi import (
    HTTPException,
    status,
    Path,
)

from . import crud
from .schemas import UserSchema


def user_by_uuid(user_uuid: Annotated[str, Path]) -> UserSchema:
    user = crud.get_user(user_uuid=user_uuid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found",
        )
    return user
