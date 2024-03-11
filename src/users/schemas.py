from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, SecretStr

from models.role import Role


class UserCreateSchema(BaseModel):
    name: str = Field(..., max_length=50)
    surname: str = Field(..., max_length=50)
    username: str = Field(..., max_length=50)
    password: SecretStr = Field(..., max_length=128)
    phone_number: str = Field(..., max_length=20)
    email: EmailStr
    role: Role
    group_name: str | None = Field(default=None, max_length=255)


class UserSchema(UserCreateSchema):
    is_blocked: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime | None = None


class UserUpdatePartialSchema(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    surname: str | None = Field(default=None, max_length=50)
    username: str | None = Field(default=None, max_length=50)
    phone_number: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    role: Role | None = None
    group_name: str | None = Field(default=None, max_length=50)
