from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    """Base profile schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""

    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile."""

    pass


class ProfileResponse(ProfileBase):
    """Schema for profile response."""

    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
