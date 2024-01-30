from pydantic import UUID4, BaseModel


class User(BaseModel):
    username: str
    password: str
    email: str | None = None
    active: bool = True


class UserSignup(User):
    pass


class UserLogin(User):
    password: bytes


class UserCreate(User):
    id: UUID4
