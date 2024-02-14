from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import (
    check_if_user_exists_with_this_email_or_username,
    create_user,
    get_or_create_group,
    get_user_by_username,
)
from auth.schemas import UserLoginSchema
from auth.tokens_utils import generate_tokens, verify_refresh_token
from integrations.localstack.localstack import s3_client
from integrations.rabbitmq.consumer import get_single_message
from integrations.rabbitmq.publisher import publish_message
from models import User
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

    return generate_tokens(payload)


def refresh_token_controller(refresh_token: str):
    payload = verify_refresh_token(refresh_token)
    return generate_tokens(payload)


def reset_password_controller(email: str):
    try:
        # how to generate link?
        link = "https://yourwebsite.com/reset-password-token"

        current_datetime = str(datetime.utcnow())

        message = {
            "email": email,
            "subject": "Reset your password",
            "body": f"Click the following link to reset your password: {link}",
            "publishing_datetime": current_datetime,
        }
        publish_message(
            queue="reset-password-queue",
            exchange="reset-password-exchange",
            routing_key="reset-password-routing_key",
            message=message,
        )
        return {"message": f"Password reset email sent on {email}."}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred.",
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
