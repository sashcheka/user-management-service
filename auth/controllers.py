from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.crud import create_user, get_or_create_group
from auth.rabbitmq_consumer import get_single_message
from auth.rabbitmq_publisher import publish_message
from auth.schemas import UserLoginSchema
from auth.tokens_utils import generate_tokens, verify_refresh_token
from models import User
from users.schemas import UserCreateSchema


async def create_user_controller(
    session: AsyncSession,
    user_in: UserCreateSchema,
) -> User:
    group = await get_or_create_group(session=session, user_in=user_in)
    user = await create_user(session=session, user_in=user_in)
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred: " + str(e),
        )


def consume_test_message_controller():
    try:
        message = get_single_message(queue="reset-password-queue")
        if message:
            return {"message": "Message consumed", "data": message}
        else:
            return {"message": "No messages in the queue."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred: " + str(e),
        )
