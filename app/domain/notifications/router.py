import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, get_user_repository
from app.domain.notifications.models import NotificationStatus
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import (
    NotificationCreate,
    NotificationListResponse,
    NotificationMarkAsRead,
    NotificationResponse,
    NotificationUpdate,
)
from app.domain.notifications.service import NotificationService
from app.domain.users.repository import UserRepository
from app.domain.users.schemas import UserResponse as CurrentUser
from app.utils.exceptions import AppException

router = APIRouter(prefix="/notifications", tags=["notifications"])


async def get_notification_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> NotificationService:
    """
    Get notification service dependency.

    Args:
        db: Database session
        user_repo: User repository

    Returns:
        NotificationService: The notification service
    """
    notification_repo = NotificationRepository(db)
    return NotificationService(notification_repo, user_repo)


@router.post("/", response_model=NotificationResponse)
async def send_notification(
    notification_data: NotificationCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> NotificationResponse:
    """
    Send a notification to a user.

    Args:
        notification_data: Notification data
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        NotificationResponse: The created notification
    """
    # Set the user_id to the current user's ID
    notification_data.user_id = uuid.UUID(str(current_user.id))
    notification = await notification_service.send_notification(notification_data)
    return NotificationResponse.model_validate(notification)


@router.get("/", response_model=NotificationListResponse)
async def get_my_notifications(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
    status: NotificationStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> NotificationListResponse:
    """
    Get notifications for the current user.

    Args:
        current_user: The current authenticated user
        notification_service: The notification service
        status: Optional status filter
        skip: Number of notifications to skip
        limit: Maximum number of notifications to return

    Returns:
        NotificationListResponse: List of notifications
    """
    notifications = await notification_service.get_user_notifications(
        uuid.UUID(str(current_user.id)), status, skip, limit
    )
    total = len(notifications)

    # Convert Notification objects to NotificationResponse objects
    notification_responses = [
        NotificationResponse.model_validate(notification)
        for notification in notifications
    ]

    return NotificationListResponse(notifications=notification_responses, total=total)


@router.get("/unread-count", response_model=int)
async def get_my_unread_count(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> int:
    """
    Get the count of unread notifications for the current user.

    Args:
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        int: Count of unread notifications
    """
    return await notification_service.get_unread_count(uuid.UUID(str(current_user.id)))


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: uuid.UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> NotificationResponse:
    """
    Get a specific notification.

    Args:
        notification_id: The notification ID
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        NotificationResponse: The requested notification

    Raises:
        HTTPException: If notification not found or access denied
    """
    try:
        notification = await notification_service.get_notification_by_id(
            notification_id
        )
        # Check if user owns the notification
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        return NotificationResponse.model_validate(notification)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: uuid.UUID,
    notification_update: NotificationUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> NotificationResponse:
    """
    Update a notification.

    Args:
        notification_id: The notification ID
        notification_update: Notification update data
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        NotificationResponse: The updated notification

    Raises:
        HTTPException: If notification not found or access denied
    """
    try:
        # First get the notification to check ownership
        notification = await notification_service.get_notification_by_id(
            notification_id
        )
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        updated_notification = await notification_service.update_notification(
            notification_id, notification_update
        )
        return NotificationResponse.model_validate(updated_notification)
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.post("/mark-as-read", response_model=dict)
async def mark_notifications_as_read(
    mark_as_read: NotificationMarkAsRead,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> dict:
    """
    Mark multiple notifications as read.

    Args:
        mark_as_read: Notification IDs to mark as read
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        dict: Success message

    Raises:
        HTTPException: If any notification not found or access denied
    """
    try:
        # Verify all notifications belong to the current user
        for notification_id in mark_as_read.notification_ids:
            notification = await notification_service.get_notification_by_id(
                notification_id
            )
            if notification.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")

        await notification_service.mark_notifications_as_read(
            mark_as_read.notification_ids
        )
        return {"message": "Notifications marked as read successfully"}
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e


@router.delete("/{notification_id}", response_model=dict)
async def delete_notification(
    notification_id: uuid.UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    notification_service: Annotated[
        NotificationService, Depends(get_notification_service)
    ],
) -> dict:
    """
    Delete a notification.

    Args:
        notification_id: The notification ID
        current_user: The current authenticated user
        notification_service: The notification service

    Returns:
        dict: Success message

    Raises:
        HTTPException: If notification not found or access denied
    """
    try:
        # First get the notification to check ownership
        notification = await notification_service.get_notification_by_id(
            notification_id
        )
        if notification.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        await notification_service.delete_notification(notification_id)
        return {"message": "Notification deleted successfully"}
    except AppException as e:
        raise HTTPException(status_code=404, detail=e.message) from e
