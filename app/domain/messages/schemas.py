from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MessageBase(BaseModel):
    """Base message schema."""

    subject: Optional[str] = Field(None, max_length=255)
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    recipient_id: UUID


class MessageUpdate(BaseModel):
    """Schema for updating a message."""

    subject: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1)


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: UUID
    sender_id: UUID
    recipient_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageListResponse(BaseModel):
    """Schema for message list response."""

    messages: List[MessageResponse]
    total: int


class MessageSendRequest(MessageBase):
    """Schema for sending a message request."""

    recipient_id: UUID
