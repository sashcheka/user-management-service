from datetime import datetime
from typing import List

from fastapi import HTTPException, UploadFile, status
from pydantic import UUID4
from sqlalchemy import asc, desc, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import get_or_create_group
from models import Role
from models.user import User

from .schemas import UserUpdatePartialSchema


async def update_user(
    session: AsyncSession,
    user_update: UserUpdatePartialSchema,
    user: User,
    partial: bool = False,
) -> User:
    update_data = user_update.model_dump(exclude_unset=partial)
    for key, value in update_data.items():
        if key == "group_name" and value is not None:
            group = await get_or_create_group(session, user_in=user_update)
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Group '{value}' does not exist and could not be created.",
                )
        elif not partial or (partial and value is not None):
            setattr(user, key, value)

    user.modified_at = datetime.utcnow()

    try:
        await session.commit()
        return user
    except IntegrityError as e:
        handle_integrity_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred.",
        )


def handle_integrity_error(e):
    error_detail = f"A record with similar data already exists. Error: {e}"
    if "username" in str(e.orig):
        error_detail = "A user with this USERNAME already exists."
    elif "email" in str(e.orig):
        error_detail = "A user with this EMAIL already exists."
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error_detail,
    )


async def get_user(
    session: AsyncSession,
    user_id: UUID4,
) -> User | None:
    return await session.get(User, user_id)


async def delete_user(
    session: AsyncSession,
    user: User,
):
    await session.delete(user)
    await session.commit()
    return {"detail": f"User {user.name} successfully deleted"}


async def list_users(
    session: AsyncSession,
    page: int,
    limit: int,
    filter_by_name: str,
    sort_by: str,
    order_by: str,
    current_user: User,
) -> List[User]:
    offset = (page - 1) * limit
    query = select(User)

    if filter_by_name:
        name_filter = f"%{filter_by_name}%"
        query = query.where(
            or_(
                User.name.ilike(name_filter),
                User.surname.ilike(name_filter),
            )
        )

    if current_user.role == Role.MODERATOR:
        query = query.where(User.group_name == current_user.group_name)

    sort_column = getattr(User, sort_by)

    if order_by.lower() == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    query = query.offset(offset).limit(limit)
    result = await session.execute(query)

    return list(result.scalars().all())
