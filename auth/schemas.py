from pydantic import BaseModel, EmailStr


class UserLoginSchema(BaseModel):
    username: str = "username"
    password: str = "password"


class RefreshTokenSchema(BaseModel):
    refresh_token: str = "refresh_token"


class EmailSchema(BaseModel):
    email: EmailStr
