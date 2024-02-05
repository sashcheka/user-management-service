from pydantic import BaseModel, EmailStr


class UserLoginSchema(BaseModel):
    username: str
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class EmailSchema(BaseModel):
    email: EmailStr
