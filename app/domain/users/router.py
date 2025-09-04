import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.domain.profiles.repository import ProfileRepository
from app.domain.users.models import User
from app.domain.users.policies import check_user_access, require_admin_role
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserListResponse, UserResponse, UserUpdate
from app.domain.users.service import UserService
from app.utils.exceptions import AppException

router = APIRouter(prefix="/users", tags=["users"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(db: DBSession) -> UserService:
    """Get user service dependency."""
    user_repo = UserRepository(db)
    profile_repo = ProfileRepository(db)
    return UserService(user_repo, profile_repo)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> User:
    """
    Get current user (without profile).

    Args:
        current_user: The current authenticated user

    Returns:
        User: The current user
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """
    Get specific user.

    Args:
        user_id: The user ID
        current_user: The current authenticated user
        user_service: The user service

    Returns:
        User: The requested user

    Raises:
        HTTPException: If access is denied or user not found
    """
    # Check access
    if not check_user_access(current_user, user_id):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        return await user_service.get_user_by_id(user_id)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> User:
    """
    Update specific user.

    Args:
        user_id: The user ID
        user_update: User update data
        current_user: The current authenticated user
        user_service: The user service

    Returns:
        User: The updated user

    Raises:
        HTTPException: If access is denied or user not found
    """
    # Require admin role
    require_admin_role(current_user)

    try:
        return await user_service.update_user(user_id, user_update)
    except AppException as e:
        raise HTTPException(status_code=400, detail=e.message) from e


@router.get("/", response_model=UserListResponse)
async def list_users(
    current_user: CurrentUser,
    user_service: Annotated[UserService, Depends(get_user_service)],
    skip: int = 0,
    limit: int = 100,
) -> UserListResponse:
    """
    List all users.

    Args:
        current_user: The current authenticated user
        user_service: The user service
        skip: Number of users to skip
        limit: Maximum number of users to return

    Returns:
        UserListResponse: List of users

    Raises:
        HTTPException: If access is denied
    """
    # Require admin role
    require_admin_role(current_user)

    users = await user_service.get_all_users(skip, limit)
    total = len(users)

    # Convert User objects to UserResponse objects
    user_responses = [
        UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            role=user.role,
            is_active=bool(user.is_active),
            is_superuser=bool(user.is_superuser),
            created_at=getattr(user, "created_at", None),  # type: ignore
            updated_at=getattr(user, "updated_at", None),  # type: ignore
        )
        for user in users
    ]

    return UserListResponse(users=user_responses, total=total)
