import uuid
from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr, Field, SecretStr


class UserLoginSchema(BaseModel):
    username: str
    password: SecretStr


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class EmailSchema(BaseModel):
    email: EmailStr


class ResetPasswordMessageSchema(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    user_id: UUID4 = Field(...)
    email: EmailStr = Field(...)
    subject: str = Field(default="Reset your password")
    body: str = Field(default_factory=str)

    def generate_body(self, token: str):
        self.body = f"Link to reset your password: https://yourwebsite.com/reset-password/{token}"

    published_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: datetime | None = Field(default=None)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            UUID4: lambda x: str(x),
            datetime: lambda x: x.isoformat(),
        }
