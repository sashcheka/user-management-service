import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserLoginSchema
from core.password_utils import hash_password
from models import Group
from models.user import User
from users.schemas import UserCreateSchema


async def get_or_create_group(
    session: AsyncSession,
    user_in: UserCreateSchema,
) -> Group | None:
    group_name = user_in.group_name

    if not group_name:
        return None

    group_name = user_in.group_name
    result = await session.execute(select(Group).where(Group.name == group_name))
    group = result.scalar()

    if group:
        return group

    group = Group(name=group_name)
    session.add(group)
    await session.commit()
    return group


async def create_user(
    session: AsyncSession,
    user_in: UserCreateSchema,
    image_s3_path: str,
) -> User:
    user_data = user_in.model_dump()
    user_data["password"] = hash_password(user_data["password"])
    user_data["image_s3_path"] = image_s3_path

    try:
        user = User(**user_data)
        session.add(user)
        await session.commit()
        return user

    except IntegrityError as e:
        logging.exception(f"Failed to sign up user: {user_in.username}. Exception: {e}")

        fields_to_check = [
            "username",
            "email",
        ]
        error_detail = "A record with similar data already exists."

        for field in fields_to_check:
            if field in str(e.orig):
                error_detail = f"A user with this {field.upper()} already exists."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
        )

    except Exception as e:
        logging.error(f"Failed to sign up user: {user_in.username}. Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred.",
        )


async def get_user_by_username(
    session: AsyncSession,
    user_in: UserLoginSchema,
) -> User | None:
    result = await session.execute(
        select(User).where(User.username == user_in.username)
    )
    user = result.scalar()
    return user
