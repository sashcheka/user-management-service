from fastapi import APIRouter, Depends

from . import crud
from .dependencies import user_by_uuid
from .schemas import UserSchema, UserCreateSchema, UserUpdateSchema

router = APIRouter(prefix="/user", tags=["User"])


@router.post("/", response_model=UserSchema)
def create_user(user_in: UserCreateSchema):
    return crud.create_user(user_in)


@router.get("/{user_uuid}/", response_model=UserSchema)
def get_user(user: UserSchema = Depends(user_by_uuid)):
    return user


@router.patch("/{user_uuid/", response_model=UserSchema)
def update_user(
    user_update: UserUpdateSchema, user: UserSchema = Depends(user_by_uuid)
):
    return crud.update_user(user=user, user_update=user_update)
