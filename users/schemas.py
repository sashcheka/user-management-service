from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr

from models.role import Role


class UserCreateSchema(BaseModel):
    name: str
    surname: str
    username: str
    password: str
    phone_number: str
    email: EmailStr
    role: Role
    group_name: str | None = None
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
    group_name: str | None = None
    image_s3_path: str | None = None
    is_blocked: bool = False
    created_at: datetime = datetime.utcnow()
    modified_at: datetime | None = None


class UserUpdatePartialSchema(BaseModel):
    name: str | None = None
    surname: str | None = None
    username: str | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
    role: Role | None = None
    group_name: str | None = None
    image_s3_path: str | None = None
