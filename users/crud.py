from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from core.redis_helper import redis_client
from models.user import User

from .schemas import UserSchema, UserUpdatePartialSchema, UserUpdateSchema


async def update_user(
    session: AsyncSession,
    user_update: UserUpdatePartialSchema,
    user: UserSchema,
    partial: bool = False,
) -> UserSchema:
    for key, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, key, value)
    user.modified_at = datetime.utcnow()
    await session.commit()
    return user


async def get_user(
    session: AsyncSession,
    user_id: uuid4,
) -> User | None:
    return await session.get(User, user_id)


async def delete_user(
    session: AsyncSession,
    user: UserSchema,
    token: str,
) -> str:
    redis_client.delete(token)
    await session.delete(user)
    await session.commit()
    return f"User {user.name} deleted successfully"
