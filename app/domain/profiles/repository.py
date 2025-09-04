import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.profiles.models import Profile
from app.domain.profiles.schemas import ProfileCreate


class ProfileRepository:
    """Repository for profile-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: uuid.UUID, profile_create: ProfileCreate
    ) -> Profile:
        """
        Create a new profile.

        Args:
            user_id: The user ID
            profile_create: Profile creation schema

        Returns:
            Profile: The created profile
        """
        db_profile = Profile(
            user_id=user_id,
            first_name=profile_create.first_name,
            last_name=profile_create.last_name,
            avatar_url=profile_create.avatar_url,
            bio=profile_create.bio,
            phone=profile_create.phone,
            timezone=profile_create.timezone,
        )
        self.db.add(db_profile)
        await self.db.commit()
        await self.db.refresh(db_profile)
        return db_profile

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Profile]:
        """
        Get a profile by user ID.

        Args:
            user_id: The user ID

        Returns:
            Profile: The profile if found, None otherwise
        """
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(self, profile: Profile, **kwargs) -> Profile:
        """
        Update a profile.

        Args:
            profile: The profile to update
            **kwargs: Fields to update

        Returns:
            Profile: The updated profile
        """
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def delete(self, profile: Profile) -> None:
        """
        Delete a profile.

        Args:
            profile: The profile to delete
        """
        await self.db.delete(profile)
        await self.db.commit()
