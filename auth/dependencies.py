from fastapi import Depends, Form, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.tokens_utils import decode_jwt
from core.db_helper import db_helper
from models import Role, User
from users.crud import get_user
from users.schemas import UserCreateSchema

security = HTTPBearer()


async def get_auth_user_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


async def get_auth_user(
    payload: dict = Depends(get_auth_user_payload),
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user_id = payload.get("sub")
    # stmt = select(User).where(User.id == user_id)
    # result = await session.execute(stmt)
    # user: User = result.scalar()

    user = await get_user(session=session, user_id=user_id)

    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
    )


def get_active_auth_user(
    user: User = Depends(get_auth_user),
) -> User:
    if not user.is_blocked:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User inactive",
    )


def get_user_signup_data(
    name: str = Form(default="name", max_length=50),
    surname: str = Form(default="surname", max_length=50),
    username: str = Form(default="username", max_length=50),
    password: str = Form(default="password", max_length=128),
    phone_number: str = Form(default="123-456-7890", max_length=20),
    email: EmailStr = Form(default="email@example.com"),
    role: Role = Form(default=Role.USER),
    group_name: str = Form(default=None, max_length=255),
) -> UserCreateSchema:
    return UserCreateSchema(
        name=name,
        surname=surname,
        username=username,
        password=password,
        phone_number=phone_number,
        email=email,
        role=Role(role),
        group_name=group_name,
    )
