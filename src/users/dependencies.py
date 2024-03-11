from typing import Annotated

from fastapi import Depends, Form, HTTPException, Path, Query, UploadFile, status
from pydantic import UUID4, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_active_auth_user
from core.db_helper import db_helper
from integrations.localstack.localstack import s3_client
from models import User
from models.role import Role

from . import crud
from .query_params import UsersListQueryParams
from .schemas import UserUpdatePartialSchema


async def user_by_id(
    user_id: Annotated[UUID4, Path],
    session: AsyncSession = Depends(db_helper.scoped_session_dependencies),
) -> User:
    user = await crud.get_user(session=session, user_id=user_id)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id: {user_id} not found",
    )


def verify_admin_or_moderator_access(
    current_user: User = Depends(get_active_auth_user),
):
    if current_user.role in (Role.ADMIN, Role.MODERATOR):
        return True

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )


def get_users_list_query_params(
    page: int = Query(1, gt=0, lt=100),
    limit: int = Query(10, gt=0, lt=100),
    filter_by_name: str | None = Query(None),
    sort_by: str = Query("username"),
    order_by: str = Query("asc"),
) -> UsersListQueryParams:
    return UsersListQueryParams(
        page=page,
        limit=limit,
        filter_by_name=filter_by_name,
        sort_by=sort_by,
        order_by=order_by,
    )


def get_user_update_data(
    name: str | None = Form(default=None, max_length=50),
    surname: str | None = Form(default=None, max_length=50),
    username: str | None = Form(default=None, max_length=50),
    phone_number: str | None = Form(default=None, max_length=20),
    email: EmailStr | None = Form(default=None),
    role: Role | None = Form(default=None),
    group_name: str | None = Form(default=None, max_length=255),
) -> UserUpdatePartialSchema:
    return UserUpdatePartialSchema(
        name=name,
        surname=surname,
        username=username,
        phone_number=phone_number,
        email=email,
        role=role,
        group_name=group_name,
    )


async def upload_new_image_and_get_path(image: UploadFile):
    try:
        image_file = await image.read(size=image.size)
        new_image_s3_path = await s3_client.upload_image_to_localstack_and_get_path(
            image_file=image_file
        )
        return new_image_s3_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload the new image to S3. {e}",
        )


async def delete_image_if_exists(image_s3_path: str):
    if image_s3_path:
        try:
            await s3_client.delete_image_from_localstack(image_path=image_s3_path)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete the old image from S3. {e}",
            )
