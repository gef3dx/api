import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.domain.profiles.models import Profile
from app.domain.profiles.repository import ProfileRepository
from app.domain.profiles.schemas import ProfileResponse, ProfileUpdate
from app.domain.profiles.service import ProfileService
from app.domain.users.models import User
from app.domain.users.policies import check_profile_access, require_admin_role
from app.utils.exceptions import AppException

router = APIRouter(prefix="/profiles", tags=["profiles"])

DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_profile_service(db: DBSession) -> ProfileService:
    """Get profile service dependency."""
    profile_repo = ProfileRepository(db)
    return ProfileService(profile_repo)


@router.get("/me", response_model=ProfileResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Profile:
    """
    Get current user's profile.

    Args:
        current_user: The current authenticated user
        profile_service: The profile service

    Returns:
        Profile: The current user's profile

    Raises:
        HTTPException: If profile not found
    """
    try:
        return await profile_service.get_profile_by_user_id(
            uuid.UUID(str(current_user.id))
        )
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.patch("/me", response_model=ProfileResponse)
async def update_current_user_profile(
    profile_update: ProfileUpdate,
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Profile:
    """
    Update current user's profile.

    Args:
        profile_update: Profile update data
        current_user: The current authenticated user
        profile_service: The profile service

    Returns:
        Profile: The updated profile

    Raises:
        HTTPException: If profile not found
    """
    try:
        return await profile_service.update_profile(
            uuid.UUID(str(current_user.id)), profile_update
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Profile:
    """
    Get specific user's profile.

    Args:
        user_id: The user ID
        current_user: The current authenticated user
        profile_service: The profile service

    Returns:
        Profile: The requested profile

    Raises:
        HTTPException: If access is denied or profile not found
    """
    # Check access
    if not check_profile_access(current_user, user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return await profile_service.get_profile_by_user_id(uuid.UUID(str(user_id)))
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.patch("/{user_id}", response_model=ProfileResponse)
async def update_user_profile(
    user_id: uuid.UUID,
    profile_update: ProfileUpdate,
    current_user: CurrentUser,
    profile_service: Annotated[ProfileService, Depends(get_profile_service)],
) -> Profile:
    """
    Update specific user's profile.

    Args:
        user_id: The user ID
        profile_update: Profile update data
        current_user: The current authenticated user
        profile_service: The profile service

    Returns:
        Profile: The updated profile

    Raises:
        HTTPException: If access is denied or profile not found
    """
    # Require admin role for updating other users' profiles
    if current_user.id != user_id:
        require_admin_role(current_user)

    try:
        return await profile_service.update_profile(
            uuid.UUID(str(user_id)), profile_update
        )
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e
