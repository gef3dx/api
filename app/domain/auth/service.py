import uuid
from datetime import datetime, timezone
from typing import Tuple

from app.core.email import send_password_reset_email
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import get_password_hash, verify_password
from app.domain.auth.repository import AuthRepository
from app.domain.auth.schemas import (
    PasswordResetConfirm,
    PasswordResetRequest,
    UserLoginRequest,
)
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserCreate
from app.domain.users.service import UserService
from app.utils.crypto import hash_token
from app.utils.exceptions import (
    AuthenticationException,
    ValidationException,
)


class AuthService:
    """Service for authentication-related business logic."""

    def __init__(
        self,
        auth_repo: AuthRepository,
        user_repo: UserRepository,
        user_service: UserService,
    ):
        self.auth_repo = auth_repo
        self.user_repo = user_repo
        self.user_service = user_service

    async def register_user(self, user_create: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_create: User creation schema

        Returns:
            User: The created user
        """
        return await self.user_service.create_user(user_create)

    async def authenticate_user(
        self, login_request: UserLoginRequest
    ) -> Tuple[User, str, str]:
        """
        Authenticate a user and return user with tokens.

        Args:
            login_request: Login request schema

        Returns:
            Tuple[User, str, str]: The user, access token, and refresh token

        Raises:
            AuthenticationException: If authentication fails
        """
        # Get user by email or username
        user = await self.user_repo.get_by_email_or_username(
            login_request.email_or_username
        )
        if not user:
            raise AuthenticationException("Invalid credentials")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("User account is deactivated")

        # Verify password
        if not verify_password(login_request.password, user.password_hash):  # type: ignore
            raise AuthenticationException("Invalid credentials")

        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token in database
        token_data = decode_token(refresh_token)
        # Convert timestamp to timezone-aware datetime
        expires_at = datetime.fromtimestamp(token_data["exp"], tz=timezone.utc)
        await self.auth_repo.create_refresh_token(
            user_id=user.id, jti=token_data["jti"], expires_at=expires_at  # type: ignore
        )

        return user, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> Tuple[str, str]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Tuple[str, str]: The new access token and refresh token

        Raises:
            AuthenticationException: If refresh token is invalid or expired
        """
        # Decode refresh token
        try:
            payload = decode_token(refresh_token)
        except Exception as e:
            raise AuthenticationException("Invalid refresh token") from e

        jti = payload.get("jti")
        if not jti:
            raise AuthenticationException("Invalid refresh token")

        # Check if refresh token exists and is not revoked
        db_refresh_token = await self.auth_repo.get_refresh_token_by_jti(jti)
        if not db_refresh_token:
            raise AuthenticationException("Invalid refresh token")

        if db_refresh_token.revoked:
            raise AuthenticationException("Refresh token has been revoked")

        # Convert naive datetime to timezone-aware for comparison
        if db_refresh_token.expires_at.tzinfo is None:
            # If database datetime is naive, compare with naive datetime
            if db_refresh_token.expires_at < datetime.now(timezone.utc).replace(
                tzinfo=None
            ):
                raise AuthenticationException("Refresh token has expired")
        else:
            # If database datetime is timezone-aware, compare with timezone-aware datetime
            if db_refresh_token.expires_at < datetime.now(timezone.utc):
                raise AuthenticationException("Refresh token has expired")

        # Get user
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid refresh token")

        user = await self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.is_active:
            raise AuthenticationException("User account is invalid")

        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Revoke old refresh token
        await self.auth_repo.revoke_refresh_token(db_refresh_token)

        # Store new refresh token in database
        token_data = decode_token(new_refresh_token)
        # Convert timestamp to timezone-aware datetime
        expires_at = datetime.fromtimestamp(token_data["exp"], tz=timezone.utc)
        await self.auth_repo.create_refresh_token(
            user_id=user.id, jti=token_data["jti"], expires_at=expires_at  # type: ignore
        )

        return new_access_token, new_refresh_token

    async def logout(self, refresh_token: str) -> None:
        """
        Revoke current refresh token.

        Args:
            refresh_token: The refresh token to revoke

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        # Decode refresh token
        try:
            payload = decode_token(refresh_token)
        except Exception as e:
            raise AuthenticationException("Invalid refresh token") from e

        jti = payload.get("jti")
        if not jti:
            raise AuthenticationException("Invalid refresh token")

        # Revoke refresh token
        db_refresh_token = await self.auth_repo.get_refresh_token_by_jti(jti)
        if db_refresh_token:
            await self.auth_repo.revoke_refresh_token(db_refresh_token)

    async def logout_all(self, user_id: uuid.UUID) -> None:
        """
        Revoke all refresh tokens for user.

        Args:
            user_id: The user ID
        """
        await self.auth_repo.revoke_all_refresh_tokens(user_id)

    async def request_password_reset(self, reset_request: PasswordResetRequest) -> None:
        """
        Request password reset email.

        Args:
            reset_request: Password reset request schema
        """
        # Get user by email
        user = await self.user_repo.get_by_email(reset_request.email)
        if not user:
            # Don't reveal if user exists or not
            return

        # Create password reset token
        reset_token = await self.auth_repo.create_password_reset_token(user.id)  # type: ignore

        # Send email (token is in reset_token.token)
        await send_password_reset_email(user.email, reset_token.token)  # type: ignore

    async def confirm_password_reset(self, reset_confirm: PasswordResetConfirm) -> None:
        """
        Confirm password reset with token.

        Args:
            reset_confirm: Password reset confirmation schema

        Raises:
            ValidationException: If token is invalid or expired
        """
        # Hash the token for lookup
        token_hash = hash_token(reset_confirm.token)

        # Get reset token
        reset_token = await self.auth_repo.get_password_reset_token_by_hash(token_hash)
        if not reset_token:
            raise ValidationException("Invalid or expired reset token")

        # Check if token is already used
        if reset_token.used:
            raise ValidationException("Reset token has already been used")

        # Check if token is expired
        # Convert naive datetime to timezone-aware for comparison
        if reset_token.expires_at.tzinfo is None:
            # If database datetime is naive, compare with naive datetime
            if reset_token.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
                raise ValidationException("Reset token has expired")
        else:
            # If database datetime is timezone-aware, compare with timezone-aware datetime
            if reset_token.expires_at < datetime.now(timezone.utc):
                raise ValidationException("Reset token has expired")

        # Get user
        user = await self.user_repo.get_by_id(uuid.UUID(str(reset_token.user_id)))
        if not user:
            raise ValidationException("User not found")

        # Update password
        user.password_hash = get_password_hash(reset_confirm.new_password)  # type: ignore
        await self.user_repo.update(user)

        # Mark token as used
        await self.auth_repo.use_password_reset_token(reset_token)
