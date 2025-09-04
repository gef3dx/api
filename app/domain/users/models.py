import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Enum, Index, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.domain.users.enums import UserRole

if TYPE_CHECKING:
    pass


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role: UserRole = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)  # type: ignore
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_username", "username"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}', role='{self.role}')>"
