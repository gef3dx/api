from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.users.enums import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    role: UserRole
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Schema for user list response."""

    users: List[UserResponse]
    total: int


class UserLoginRequest(BaseModel):
    """Schema for user login request."""

    email_or_username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""

    token: str
    new_password: str = Field(..., min_length=8)
