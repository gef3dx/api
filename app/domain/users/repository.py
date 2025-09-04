import uuid
from typing import List, Optional, Union, cast, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.engine import Result as SyncResult

from app.core.security import get_password_hash
from app.domain.users.enums import UserRole
from app.domain.users.models import User
from app.domain.users.schemas import UserCreate

if TYPE_CHECKING:
    from sqlalchemy.engine import Result


class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: Union[AsyncSession, Session]):
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
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(db_user)
        else:
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    async def create(self, user_create: UserCreate) -> User:
        """
        Create a new user synchronously.

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
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(db_user)
        else:
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            User: The user if found, None otherwise
        """
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(select(User).where(User.id == user_id))
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_id_sync(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Get a user by ID synchronously.

        Args:
            user_id: The user ID

        Returns:
            User: The user if found, None otherwise
        """
        result = self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The user email

        Returns:
            User: The user if found, None otherwise
        """
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(select(User).where(User.email == email))
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(select(User).where(User.email == email))
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_email_sync(self, email: str) -> Optional[User]:
        """
        Get a user by email synchronously.

        Args:
            email: The user email

        Returns:
            User: The user if found, None otherwise
        """
        result = self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username

        Returns:
            User: The user if found, None otherwise
        """
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(select(User).where(User.username == username))
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_username_sync(self, username: str) -> Optional[User]:
        """
        Get a user by username synchronously.

        Args:
            username: The username

        Returns:
            User: The user if found, None otherwise
        """
        result = self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email_or_username(self, email_or_username: str) -> Optional[User]:
        """
        Get a user by email or username.

        Args:
            email_or_username: The email or username

        Returns:
            User: The user if found, None otherwise
        """
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(
                select(User).where(
                    (User.email == email_or_username) | (User.username == email_or_username)
                )
            )
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(
                select(User).where(
                    (User.email == email_or_username) | (User.username == email_or_username)
                )
            )
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_email_or_username_sync(self, email_or_username: str) -> Optional[User]:
        """
        Get a user by email or username synchronously.

        Args:
            email_or_username: The email or username

        Returns:
            User: The user if found, None otherwise
        """
        result = self.db.execute(
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
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(select(User).offset(skip).limit(limit))
            users = result.scalars().all()
            return list(users)
        else:
            result = self.db.execute(select(User).offset(skip).limit(limit))
            users = cast(SyncResult, result).scalars().all()
            return list(users)

    def get_all_sync(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination synchronously.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List[User]: List of users
        """
        result = self.db.execute(select(User).offset(skip).limit(limit))
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

        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(user)
        else:
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_sync(self, user: User, **kwargs) -> User:
        """
        Update a user synchronously.

        Args:
            user: The user to update
            **kwargs: Fields to update

        Returns:
            User: The updated user
        """
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """
        Delete a user.

        Args:
            user: The user to delete
        """
        if isinstance(self.db, AsyncSession):
            await self.db.delete(user)
            await self.db.commit()
        else:
            self.db.delete(user)
            self.db.commit()

    def delete_sync(self, user: User) -> None:
        """
        Delete a user synchronously.

        Args:
            user: The user to delete
        """
        self.db.delete(user)
        self.db.commit()