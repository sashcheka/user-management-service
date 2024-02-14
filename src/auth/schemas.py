from pydantic import BaseModel, EmailStr, SecretStr


class UserLoginSchema(BaseModel):
    username: str
    password: SecretStr


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class EmailSchema(BaseModel):
    email: EmailStr
