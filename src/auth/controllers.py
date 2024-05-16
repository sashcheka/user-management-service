import os
from datetime import timedelta

import jwt
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import (
    check_if_user_exists_with_this_email_or_username,
    create_user,
    get_or_create_group,
    update_user_password,
)
from auth.jwt_utils import encode_jwt
from auth.schemas import (
    PasswordChangeSchema,
    ResetPasswordMessageSchema,
    UserLoginSchema,
)
from auth.tokens_utils import (
    generate_tokens,
    get_payload_by_token,
    verify_refresh_token_and_get_payload,
)
from core.redis_helper import add_refresh_token_to_redis
from integrations.localstack.localstack import s3_client
from integrations.rabbitmq.consumer import get_single_message
from integrations.rabbitmq.publisher import publish_message
from models import User
from users.crud import get_user
from users.schemas import UserCreateSchema


async def create_user_controller(
    user_in: UserCreateSchema,
    session: AsyncSession,
    image: UploadFile,
) -> User:
    existing_user = await check_if_user_exists_with_this_email_or_username(
        session=session,
        username=user_in.username,
        email=user_in.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with this email or username already exists.",
        )

    image_file = await image.read(size=image.size)
    image_s3_path = await s3_client.upload_image_to_localstack_and_get_path(
        image_file=image_file
    )

    group = await get_or_create_group(session=session, user_in=user_in)
    user = await create_user(
        session=session,
        user_in=user_in,
        image_s3_path=image_s3_path,
    )
    return user


def login_user_controller(user: UserLoginSchema):
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
    }
    tokens = generate_tokens(payload)
    add_refresh_token_to_redis(tokens["refresh_token"])
    return tokens


def refresh_token_controller(refresh_token: str):
    payload = verify_refresh_token_and_get_payload(refresh_token)
    tokens = generate_tokens(payload)
    add_refresh_token_to_redis(tokens["refresh_token"])
    return tokens


def reset_password_controller(
    email: str,
    user: User,
):
    try:
        reset_password_message = ResetPasswordMessageSchema(
            user_id=user.id,
            email=email,
        )

        payload = {
            "sub": str(user.id),
            "username": user.username,
        }

        reset_password_token = encode_jwt(
            payload=payload,
            token_type="reset_password_token",
            expire_timedelta=timedelta(
                minutes=float(os.environ["RESET_PASSWORD_TOKEN_EXPIRE_MINUTES"]),
            ),
        )

        reset_password_message.generate_body(reset_password_token)

        publish_message(
            queue="reset-password-queue",
            exchange="reset-password-exchange",
            routing_key="reset-password-routing_key",
            message=reset_password_message,
        )

        return {"message": f"Password reset message sent on email: {email}."}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred.",
        )


def consume_message_controller():
    try:
        message = get_single_message(queue="reset-password-queue")
        if message:
            return {"message": "Message consumed", "data": message}
        else:
            return {"message": "No messages in the queue."}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred.",
        )


async def reset_password_check_controller(
    token: str,
    new_password: PasswordChangeSchema,
    session: AsyncSession,
):
    try:
        payload = get_payload_by_token(token)
        user_id = payload.get("sub")
        user = await get_user(session=session, user_id=user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        await update_user_password(
            session=session,
            user_id=user_id,
            new_password=new_password.new_password.get_secret_value(),
        )

        return {"message": "Password has been updated successfully."}

    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired."
        ) from e

    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="JWT validation error."
        ) from e

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        ) from e
