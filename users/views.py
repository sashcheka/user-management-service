from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_active_auth_user, get_auth_user
from core.db_helper import db_helper
from models import User
from .controllers import (
    update_self_user_info_partial_controller,
    delete_self_user_info_controller,
    get_user_info_controller,
    update_user_info_controller,
    delete_user_info_controller,
    list_users_info_controller,
)
from .dependencies import (
    get_users_list_query_params,
    user_by_id,
    verify_admin_or_moderator_access,
)
from .query_params import UsersListQueryParams
from .schemas import UserUpdatePartialSchema

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me/")
async def read_current_user(user: User = Depends(get_active_auth_user)):
    return user


@router.patch("/me/")
async def update_self_info_partial(
    user_update: UserUpdatePartialSchema,
    user: User = Depends(get_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await update_self_user_info_partial_controller(
        session=session,
        user=user,
        user_update=user_update,
    )


@router.delete("/me/")
async def delete_self_info(
    user: User = Depends(get_active_auth_user),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
):
    return await delete_self_user_info_controller(
        session=session,
        user=user,
    )


@router.get("/{user_id}/")
async def get_user_info(
    user: User = Depends(user_by_id),
    current_user: User = Depends(get_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    return await get_user_info_controller(
        user=user,
        current_user=current_user,
    )


@router.patch("/{user_id}/")
async def update_user_info(
    user_update: UserUpdatePartialSchema,
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: User = Depends(get_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    return await update_user_info_controller(
        user_update=user_update,
        user=user,
        session=session,
        current_user=current_user,
    )


@router.delete("/{user_id}/")
async def delete_user_info(
    user: User = Depends(user_by_id),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: User = Depends(get_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    return await delete_user_info_controller(
        user=user,
        session=session,
        current_user=current_user,
    )


# /users/
@router.get("s/")
async def list_users_info(
    query_params: UsersListQueryParams = Depends(get_users_list_query_params),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
    current_user: User = Depends(get_auth_user),
    _=Depends(verify_admin_or_moderator_access),
):
    return await list_users_info_controller(
        query_params=query_params,
        session=session,
        current_user=current_user,
    )
