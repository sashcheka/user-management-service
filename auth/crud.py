from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils import hash_password
from models import Group
from models.user import User
from users.schemas import UserCreateSchema


async def create_user(
    session: AsyncSession,
    user_in: UserCreateSchema,
) -> User:
    user_data = user_in.model_dump()
    hashed_password = hash_password(user_data["password"])
    user_data["password"] = hashed_password
    group_name = user_data.get("group_name")

    if group_name is not None:
        result = await session.execute(select(Group).where(Group.name == group_name))
        group = result.scalars().first()
        if not group:
            group = Group(name=group_name)
            session.add(group)
            await session.commit()

    try:
        user = User(**user_data)
        session.add(user)
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
