import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    pass

from app.db.base import Base
from app.domain.notifications.enums import NotificationStatus, NotificationType


class Notification(Base):
    """
    Notification model for storing user notifications.
    """

    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type: NotificationType = Column(
        Enum(NotificationType, name="notificationtype"),
        default=NotificationType.INFO,
        nullable=False,
    )  # type: ignore[assignment]
    status: NotificationStatus = Column(
        Enum(NotificationStatus, name="notificationstatus"),
        default=NotificationStatus.UNREAD,
        nullable=False,
    )  # type: ignore[assignment]
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", backref="notifications")

    # Indexes
    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_status", "status"),
        Index("ix_notifications_type", "type"),
        Index("ix_notifications_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title}', type='{self.type}', status='{self.status}')>"
