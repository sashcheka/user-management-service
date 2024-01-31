from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_auth_user,
    get_current_auth_user,
    get_current_token_payload,
    oauth2_scheme,
)
from core.db_helper import db_helper
from models.role import Role

from . import crud
from .dependencies import verify_admin_or_moderator_access
from .schemas import UserSchema, UserUpdatePartialSchema

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me/")
async def get_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "user": user,
        "logged_in_at": iat,
    }


@router.patch("/me/")
async def update_self_info_partial(
    user_update: UserUpdatePartialSchema,
    user: UserSchema = Depends(get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.update_user(
        session=session, user_update=user_update, user=user, partial=True
    )


@router.delete("/me/")
async def delete_self_info(
    token: str = Depends(oauth2_scheme),
    user: UserSchema = Depends(get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.delete_user(session=session, user=user, token=token)


@router.get("/{user_id}/")
async def get_user_info(
    user_id: UUID4,
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: UserSchema = Depends(get_current_auth_user),
    __=Depends(verify_admin_or_moderator_access),
):
    user = await crud.get_user(session=session, user_id=user_id)

    if (
        current_user.role == Role.MODERATOR
        and current_user.group_name != user.group_name
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
