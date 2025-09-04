import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models import PasswordResetToken, RefreshToken
from app.utils.crypto import generate_token, hash_token


class AuthRepository:
    """Repository for authentication-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_refresh_token(
        self, user_id: uuid.UUID, jti: str, expires_at: datetime
    ) -> RefreshToken:
        """
        Create a new refresh token.

        Args:
            user_id: The user ID
            jti: The JWT ID
            expires_at: The expiration datetime

        Returns:
            RefreshToken: The created refresh token
        """
        db_refresh_token = RefreshToken(user_id=user_id, jti=jti, expires_at=expires_at)
        self.db.add(db_refresh_token)
        await self.db.commit()
        await self.db.refresh(db_refresh_token)
        return db_refresh_token

    async def get_refresh_token_by_jti(self, jti: str) -> Optional[RefreshToken]:
        """
        Get a refresh token by JTI.

        Args:
            jti: The JWT ID

        Returns:
            RefreshToken: The refresh token if found, None otherwise
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        """
        Revoke a refresh token.

        Args:
            refresh_token: The refresh token to revoke

        Returns:
            RefreshToken: The revoked refresh token
        """
        refresh_token.revoked = True  # type: ignore
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        """
        Revoke all refresh tokens for a user.

        Args:
            user_id: The user ID
        """
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        refresh_tokens = result.scalars().all()

        for token in refresh_tokens:
            token.revoked = True  # type: ignore

        await self.db.commit()

    async def create_password_reset_token(
        self, user_id: uuid.UUID
    ) -> PasswordResetToken:
        """
        Create a new password reset token.

        Args:
            user_id: The user ID

        Returns:
            PasswordResetToken: The created password reset token
        """
        # Generate a secure token
        token = generate_token()
        token_hash = hash_token(token)

        # Set expiration (1 hour)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        db_reset_token = PasswordResetToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at, used=False
        )
        self.db.add(db_reset_token)
        await self.db.commit()
        await self.db.refresh(db_reset_token)

        # Return the token (not the hash) so it can be sent to the user
        db_reset_token.token = token  # Add the token temporarily for return
        return db_reset_token

    async def get_password_reset_token_by_hash(
        self, token_hash: str
    ) -> Optional[PasswordResetToken]:
        """
        Get a password reset token by hash.

        Args:
            token_hash: The token hash

        Returns:
            PasswordResetToken: The password reset token if found, None otherwise
        """
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def use_password_reset_token(
        self, reset_token: PasswordResetToken
    ) -> PasswordResetToken:
        """
        Mark a password reset token as used.

        Args:
            reset_token: The password reset token to mark as used

        Returns:
            PasswordResetToken: The updated password reset token
        """
        reset_token.used = True  # type: ignore
        await self.db.commit()
        await self.db.refresh(reset_token)
        return reset_token
