from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_auth_user,
    get_current_auth_user,
    get_current_token_payload,
)
from core.db_helper import db_helper
from models import User
from models.role import Role

from . import crud
from .dependencies import user_by_id, verify_admin_or_moderator_access
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
    user: User = Depends(get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.update_user(
        session=session,
        user_update=user_update,
        user=user,
        partial=True,
    )


@router.delete("/me/")
async def delete_self_info(
    user: UserSchema = Depends(get_current_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    user_to_delete = User(**user.model_dump())
    return await crud.delete_user(session=session, user=user_to_delete)


@router.get("/users/")
async def list_users(
    page: int = Query(1, gt=0, lt=100),
    limit: int = Query(10, gt=0, lt=100),
    filter_by_name: str | None = None,
    sort_by: str = Query("username"),
    order_by: str = Query("asc"),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: UserSchema = Depends(get_current_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    offset = (page - 1) * limit

    query = select(User)

    if filter_by_name:
        query = query.where(
            or_(
                User.name.ilike(f"%{filter_by_name}%"),
                User.surname.ilike(f"%{filter_by_name}%"),
            )
        )

    if current_user.role == Role.MODERATOR:
        query = query.where(User.group_name == current_user.group_name)

    order_function = desc if order_by.lower() == "desc" else asc
    query = query.order_by(order_function(getattr(User, sort_by)))

    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    users = result.scalars().all()

    return users


@router.get("/{user_id}/")
async def get_user_info(
    user: User = Depends(user_by_id),
    current_user: UserSchema = Depends(get_current_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if (
        current_user.role == Role.MODERATOR
        and current_user.group_name != user.group_name
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    return user


@router.patch("/{user_id}/")
async def update_user_info(
    user_update: UserUpdatePartialSchema,
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: UserSchema = Depends(get_current_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this resource.",
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    updated_user = await crud.update_user(
        session=session,
        user=user,
        user_update=user_update,
        partial=True,
    )

    return updated_user


@router.delete("/{user_id}/")
async def delete_user(
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: UserSchema = Depends(get_current_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this resource.",
        )

    deleted_user = await crud.delete_user(session=session, user=user)

    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already deleted",
        )

    return {"user": user, "detail": "User successfully deleted"}
