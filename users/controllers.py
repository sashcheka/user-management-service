from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List
from models.role import Role
from . import crud
from .query_params import UsersListQueryParams
from .schemas import UserUpdatePartialSchema
from models import User
from .utils import require_role, ensure_user_exists


async def update_self_user_info_partial_controller(
    user_update: UserUpdatePartialSchema,
    user: User,
    session: AsyncSession,
) -> User:
    updated_user = await crud.update_user(
        session=session,
        user=user,
        user_update=user_update,
        partial=True,
    )

    return updated_user


async def delete_self_user_info_controller(
    user: User,
    session: AsyncSession,
):
    return await crud.delete_user(session=session, user=user)


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
):
    require_role(
        user=current_user,
        required_role=Role.ADMIN,
    )
    ensure_user_exists(user)

    updated_user = await crud.update_user(
        session=session,
        user=user,
        user_update=user_update,
        partial=True,
    )

    return updated_user


async def delete_user_info_controller(
    user: User,
    session: AsyncSession,
    current_user: User,
):
    require_role(
        user=current_user,
        required_role=Role.ADMIN,
    )
    ensure_user_exists(user)

    try:
        return await crud.delete_user(
            session=session,
            user=user,
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


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


# async def list_users_info_controller(
#     query_params: UsersListQueryParams,
#     session: AsyncSession,
#     current_user: User,
# ):
#     offset = (query_params.page - 1) * query_params.limit
#
#     query = select(User)
#
#     if query_params.filter_by_name:
#         query = query.where(
#             or_(
#                 User.name.ilike(f"%{query_params.filter_by_name}%"),
#                 User.surname.ilike(f"%{query_params.filter_by_name}%"),
#             )
#         )
#
#     if current_user.role == Role.MODERATOR:
#         query = query.where(User.group_name == current_user.group_name)
#
#     order_function = desc if query_params.order_by.lower() == "desc" else asc
#     query = query.order_by(order_function(getattr(User, query_params.sort_by)))
#
#     query = query.offset(offset).limit(query_params.limit)
#
#     result = await session.execute(query)
#     users = result.scalars().all()
#
#     return users
