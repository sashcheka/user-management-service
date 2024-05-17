from typing import List

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from models.role import Role

from . import crud
from .dependencies import delete_image_if_exists, upload_new_image_and_get_path
from .query_params import UsersListQueryParams
from .schemas import UserUpdatePartialSchema
from .utils import ensure_user_exists, require_role


async def update_self_user_info_partial_controller(
    user_update: UserUpdatePartialSchema,
    user: User,
    session: AsyncSession,
    image: UploadFile = None,
) -> User:
    old_image_s3_path = user.image_s3_path

    if image:
        new_image_s3_path = await upload_new_image_and_get_path(image)
        if new_image_s3_path:
            user.image_s3_path = new_image_s3_path
            await delete_image_if_exists(old_image_s3_path)

    updated_user = await crud.update_user(
        session=session, user=user, user_update=user_update, partial=True
    )

    return updated_user


async def delete_self_user_info_controller(
    user: User,
    session: AsyncSession,
) -> User:
    deleted_user = await crud.delete_user(session=session, user=user)
    await delete_image_if_exists(user.image_s3_path)
    return deleted_user


async def get_user_info_controller(
    user: User,
    current_user: User,
):
    ensure_user_exists(user)

    if (
        current_user.role == Role.MODERATOR
        and current_user.group_name != user.group_name
    ):
        require_role(
            user=current_user,
            required_role=Role.ADMIN,
        )

    return user


async def update_user_info_controller(
    user_update: UserUpdatePartialSchema,
    user: User,
    session: AsyncSession,
    current_user: User,
    image: UploadFile = None,
) -> User:
    require_role(user=current_user, required_role=Role.ADMIN)
    ensure_user_exists(user)

    if image:
        user.image_s3_path = await upload_new_image_and_get_path(image)

    updated_user = await crud.update_user(
        session=session, user=user, user_update=user_update, partial=True
    )

    await delete_image_if_exists(user.image_s3_path)
    return updated_user


async def delete_user_info_controller(
    user: User,
    session: AsyncSession,
    current_user: User,
) -> User:
    require_role(user=current_user, required_role=Role.ADMIN)
    ensure_user_exists(user)

    deleted_user = await crud.delete_user(session=session, user=user)
    await delete_image_if_exists(user.image_s3_path)
    return deleted_user


async def list_users_info_controller(
    query_params: UsersListQueryParams,
    session: AsyncSession,
    current_user: User,
) -> List[User]:
    return await crud.list_users(
        session=session,
        page=query_params.page,
        limit=query_params.limit,
        filter_by_name=query_params.filter_by_name,
        sort_by=query_params.sort_by,
        order_by=query_params.order_by,
        current_user=current_user,
    )
