import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base
from .role import Role

if TYPE_CHECKING:
    from .group import Group


class User(Base):
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    role: Mapped["Role"] = mapped_column(Enum(Role), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=True)
    image_s3_path: Mapped[str] = mapped_column(String(255), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow(), server_default=func.now()
    )
    modified_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        server_default=None,
        onupdate=func.now(),
        nullable=True,
    )

    group: Mapped["Group"] = relationship("Group", back_populates="users")
