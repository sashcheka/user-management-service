from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    username: str
    password: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str
