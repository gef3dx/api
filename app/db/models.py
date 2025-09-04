import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from app.db.base import Base

# Import all models to ensure they are registered with the metadata
# This ensures that all models are included in the metadata for migrations

if TYPE_CHECKING:
    pass


class RefreshToken(Base):
    """Refresh token model for JWT token revocation."""

    __tablename__ = "refresh_tokens"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        postgresql.UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    jti = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        postgresql.UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)

    # Temporary attribute for returning the token (not stored in DB)
    token: str = ""

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")



