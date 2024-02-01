from datetime import datetime

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

from .schemas import UserUpdatePartialSchema


async def update_user(
    session: AsyncSession,
    user_update: UserUpdatePartialSchema,
    user: User,
    partial: bool = False,
) -> User:
    for key, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, key, value)
    user.modified_at = datetime.utcnow()
    # await session.commit()

    try:
        await session.commit()
        return user

    except IntegrityError as e:
        await session.rollback()

        if "username" in str(e.orig):
            error_detail = "A user with this USERNAME already exists."
        elif "email" in str(e.orig):
            error_detail = "A user with this EMAIL already exists."
        else:
            error_detail = "A record with similar data already exists."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
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
