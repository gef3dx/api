import uuid

from app.domain.profiles.models import Profile
from app.domain.profiles.repository import ProfileRepository
from app.domain.profiles.schemas import ProfileUpdate
from app.utils.exceptions import NotFoundException


class ProfileService:
    """Service for profile-related business logic."""

    def __init__(self, profile_repo: ProfileRepository):
        self.profile_repo = profile_repo

    async def get_profile_by_user_id(self, user_id: uuid.UUID) -> Profile:
        """
        Get a profile by user ID.

        Args:
            user_id: The user ID

        Returns:
            Profile: The profile

        Raises:
            NotFoundException: If profile not found
        """
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundException("Profile not found", {"user_id": str(user_id)})
        return profile

    async def update_profile(
        self, user_id: uuid.UUID, profile_update: ProfileUpdate
    ) -> Profile:
        """
        Update a profile.

        Args:
            user_id: The user ID
            profile_update: Profile update schema

        Returns:
            Profile: The updated profile

        Raises:
            NotFoundException: If profile not found
        """
        profile = await self.get_profile_by_user_id(user_id)
        update_data = profile_update.dict(exclude_unset=True)
        return await self.profile_repo.update(profile, **update_data)

    async def delete_profile(self, user_id: uuid.UUID) -> None:
        """
        Delete a profile.

        Args:
            user_id: The user ID

        Raises:
            NotFoundException: If profile not found
        """
        profile = await self.get_profile_by_user_id(user_id)
        await self.profile_repo.delete(profile)
