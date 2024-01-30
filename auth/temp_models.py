from pydantic import UUID4, BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None
    active: bool = True


class UserSignup(User):
    pass


class UserLogin(User):
    password: bytes


class UserCreate(User):
    id: UUID4
    password: bytes
