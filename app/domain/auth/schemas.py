from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)


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
