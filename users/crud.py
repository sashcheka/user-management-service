from uuid import uuid4
from .schemas import UserCreateSchema, UserSchema, UserUpdateSchema
from typing import Dict

users_db: Dict[str, UserSchema] = {}


def create_user(user_in: UserCreateSchema) -> UserSchema:
    user_uuid = str(uuid4())
    user_data = user_in.model_dump()
    user_data["uuid"] = user_uuid
    user = UserSchema(**user_data)
    users_db[user_uuid] = user
    return user


def get_user(user_uuid: str) -> UserSchema | None:
    return users_db.get(user_uuid)


def update_user(
    user: UserSchema,
    user_update: UserUpdateSchema,
    partial: bool = False,
) -> UserSchema:
    for key, value in user_update.model_dump(exclude_unset=partial).items():
        setattr(user, key, value)
    return user
