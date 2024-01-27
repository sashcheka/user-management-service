from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, EmailStr, UUID4

from models.role import Role


class UserCreateSchema(BaseModel):
    name: str
    surname: str
    username: str
    password: str
    phone_number: str
    email: EmailStr
    role: Role
    image_s3_path: str | None = None


class UserSchema(BaseModel):
    id: UUID4
    name: str
    surname: str
    username: str
    password: str
    phone_number: str
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
    password: str
    phone_number: str
    email: EmailStr
    role: Role
    image_s3_path: str | None = None


class UserUpdatePartialSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    username: str | None = None
    password: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    role: Role | None = None
    image_s3_path: str | None = None
