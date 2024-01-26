from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

from models.role import Role


class UserCreateSchema(BaseModel):
    name: str
    surname: str
    username: str
    email: EmailStr
    role: Role
    image_s3_path: str | None = None


class UserSchema(BaseModel):
    uuid: UUID
    name: str
    surname: str
    username: str
    email: EmailStr
    role: Role
    group_id: int | None = None
    image_s3_path: str | None = None
    is_blocked: bool = False
    created_at: datetime = datetime.utcnow()
    modified_at: datetime | None = None


class UserUpdateSchema(BaseModel):
    name: str
    surname: str
    username: str
    email: EmailStr
    group_id: int | None = None
    image_s3_path: str | None = None
