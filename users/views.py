from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db_helper import db_helper

from . import crud
from .dependencies import user_by_id
from .schemas import (
    UserCreateSchema,
    UserSchema,
    UserUpdatePartialSchema,
    UserUpdateSchema,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/", response_model=UserSchema)
async def create_user(
    user_in: UserCreateSchema,
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.create_user(session=session, user_in=user_in)


@router.get("/{user_id}/", response_model=UserSchema)
async def get_user(user: UserSchema = Depends(user_by_id)):
    return user


@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_update: UserUpdateSchema,
    user: UserSchema = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.update_user(session=session, user=user, user_update=user_update)


@router.patch("/{user_id/", response_model=UserSchema)
async def update_user_partial(
    user_update: UserUpdatePartialSchema,
    user: UserSchema = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.update_user(
        session=session, user=user, user_update=user_update, partial=True
    )


@router.delete("/{user_id}")
async def delete_user(
    user: UserSchema = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await crud.delete_user(session=session, user=user)
