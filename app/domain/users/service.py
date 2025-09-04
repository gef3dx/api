import uuid
from typing import List

from app.domain.profiles.repository import ProfileRepository
from app.domain.profiles.schemas import ProfileCreate
from app.domain.users.models import User
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserCreate, UserUpdate
from app.utils.exceptions import ConflictException, NotFoundException


class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repo: UserRepository, profile_repo: ProfileRepository):
        self.user_repo = user_repo
        self.profile_repo = profile_repo

    async def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user with an empty profile.

        Args:
            user_create: User creation schema

        Returns:
            User: The created user

        Raises:
            ConflictException: If email or username already exists
        """
        # Check if user with email already exists
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise ConflictException(
                "User with this email already exists", {"email": user_create.email}
            )

        # Check if user with username already exists
        existing_user = await self.user_repo.get_by_username(user_create.username)
        if existing_user:
            raise ConflictException(
                "User with this username already exists",
                {"username": user_create.username},
            )

        # Create user
        user = await self.user_repo.create(user_create)

        # Create empty profile
        profile_create = ProfileCreate()
        await self.profile_repo.create(user.id, profile_create)  # type: ignore

        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            User: The user

        Raises:
            NotFoundException: If user not found
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found", {"user_id": str(user_id)})
        return user

    async def get_user_by_email(self, email: str) -> User:
        """
        Get a user by email.

        Args:
            email: The user email

        Returns:
            User: The user

        Raises:
            NotFoundException: If user not found
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise NotFoundException("User not found", {"email": email})
        return user

    async def get_user_by_username(self, username: str) -> User:
        """
        Get a user by username.

        Args:
            username: The username

        Returns:
            User: The user

        Raises:
            NotFoundException: If user not found
        """
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise NotFoundException("User not found", {"username": username})
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List[User]: List of users
        """
        return await self.user_repo.get_all(skip, limit)

    async def update_user(self, user_id: uuid.UUID, user_update: UserUpdate) -> User:
        """
        Update a user.

        Args:
            user_id: The user ID
            user_update: User update schema

        Returns:
            User: The updated user

        Raises:
            NotFoundException: If user not found
            ConflictException: If email or username already exists
        """
        user = await self.get_user_by_id(user_id)

        # Check if email is being updated and already exists
        if user_update.email and user_update.email != user.email:
            existing_user = await self.user_repo.get_by_email(user_update.email)
            if existing_user:
                raise ConflictException(
                    "User with this email already exists", {"email": user_update.email}
                )

        # Check if username is being updated and already exists
        if user_update.username and user_update.username != user.username:
            existing_user = await self.user_repo.get_by_username(user_update.username)
            if existing_user:
                raise ConflictException(
                    "User with this username already exists",
                    {"username": user_update.username},
                )

        # Update user
        update_data = user_update.dict(exclude_unset=True)
        return await self.user_repo.update(user, **update_data)

    async def delete_user(self, user_id: uuid.UUID) -> None:
        """
        Delete a user.

        Args:
            user_id: The user ID

        Raises:
            NotFoundException: If user not found
        """
        user = await self.get_user_by_id(user_id)
        await self.user_repo.delete(user)
