from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_group, create_user
from auth.schemas import UserLoginSchema
from auth.tokens import generate_tokens, verify_refresh_token
from models import User
from users.schemas import UserCreateSchema


async def create_user_controller(
    session: AsyncSession,
    user_in: UserCreateSchema,
) -> User:
    await create_group(session=session, user_in=user_in)
    user = await create_user(session=session, user_in=user_in)
    return user


def login_user_controller(user: UserLoginSchema):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "password": user.password,
    }

    return generate_tokens(payload)


def refresh_token_controller(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    return generate_tokens(payload)
