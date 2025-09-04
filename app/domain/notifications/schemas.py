from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.notifications.models import NotificationStatus, NotificationType


class NotificationBase(BaseModel):
    """Base notification schema."""

    title: str = Field(..., max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType = NotificationType.INFO


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    user_id: UUID


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""

    title: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    type: Optional[NotificationType] = None
    status: Optional[NotificationStatus] = None
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: UUID
    user_id: UUID
    status: NotificationStatus
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema for notification list response."""

    notifications: List[NotificationResponse]
    total: int


class NotificationMarkAsRead(BaseModel):
    """Schema for marking notifications as read."""

    notification_ids: List[UUID]


class NotificationSendRequest(NotificationBase):
    """Schema for sending a notification request."""

    user_id: UUID
