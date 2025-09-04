import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash
from app.domain.users.enums import UserRole
from app.domain.users.models import User
from app.domain.users.schemas import UserCreate


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_create: UserCreate) -> User:
        """
        Create a new user.

        Args:
            user_create: User creation schema

        Returns:
            User: The created user
        """
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
            role=UserRole.CLIENT,
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            User: The user if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The user email

        Returns:
            User: The user if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username

        Returns:
            User: The user if found, None otherwise
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """
        Get a user by email or username.

        Args:
            email_or_username: The email or username

        Returns:
            User: The user if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(
                (User.email == email_or_username) | (User.username == email_or_username)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List[User]: List of users
        """
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        return list(users)

    async def update(self, user: User, **kwargs) -> User:
        """
        Update a user.

        Args:
            user: The user to update
            **kwargs: Fields to update

        Returns:
            User: The updated user
        """
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """
        Delete a user.

        Args:
            user: The user to delete
        """
        await self.db.delete(user)
        await self.db.commit()
