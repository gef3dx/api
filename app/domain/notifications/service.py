import uuid
from typing import List, Optional

from app.domain.notifications.models import Notification, NotificationStatus
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import NotificationCreate, NotificationUpdate
from app.domain.users.repository import UserRepository
from app.utils.exceptions import NotFoundException


class NotificationService:
    """Service for notification-related business logic."""

    def __init__(
        self, notification_repo: NotificationRepository, user_repo: UserRepository
    ):
        self.notification_repo = notification_repo
        self.user_repo = user_repo

    async def send_notification(
        self, notification_create: NotificationCreate
    ) -> Notification:
        """
        Send a new notification.

        Args:
            notification_create: Notification creation schema

        Returns:
            Notification: The created notification

        Raises:
            NotFoundException: If user not found
        """
        # Check if user exists
        user = await self.user_repo.get_by_id(notification_create.user_id)
        if not user:
            raise NotFoundException(
                "User not found", {"user_id": str(notification_create.user_id)}
            )

        # Create notification
        return await self.notification_repo.create(notification_create)

    async def get_notification_by_id(self, notification_id: uuid.UUID) -> Notification:
        """
        Get a notification by ID.

        Args:
            notification_id: The notification ID

        Returns:
            Notification: The notification

        Raises:
            NotFoundException: If notification not found
        """
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotFoundException(
                "Notification not found", {"notification_id": str(notification_id)}
            )
        return notification

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        """
        Get notifications for a user.

        Args:
            user_id: The user ID
            status: Optional status filter
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return

        Returns:
            List[Notification]: List of notifications
        """
        return await self.notification_repo.get_user_notifications(
            user_id, status, skip, limit
        )

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: The user ID

        Returns:
            int: Count of unread notifications
        """
        return await self.notification_repo.get_unread_count(user_id)

    async def update_notification(
        self, notification_id: uuid.UUID, notification_update: NotificationUpdate
    ) -> Notification:
        """
        Update a notification.

        Args:
            notification_id: The notification ID
            notification_update: Notification update schema

        Returns:
            Notification: The updated notification

        Raises:
            NotFoundException: If notification not found
        """
        notification = await self.get_notification_by_id(notification_id)
        update_data = notification_update.model_dump(exclude_unset=True)
        return await self.notification_repo.update(notification, **update_data)

    async def mark_notifications_as_read(
        self, notification_ids: List[uuid.UUID]
    ) -> None:
        """
        Mark multiple notifications as read.

        Args:
            notification_ids: List of notification IDs to mark as read

        Raises:
            NotFoundException: If any notification not found
        """
        # Verify all notifications exist
        for notification_id in notification_ids:
            await self.get_notification_by_id(notification_id)

        await self.notification_repo.mark_as_read(notification_ids)

    async def delete_notification(self, notification_id: uuid.UUID) -> None:
        """
        Delete a notification.

        Args:
            notification_id: The notification ID

        Raises:
            NotFoundException: If notification not found
        """
        notification = await self.get_notification_by_id(notification_id)
        await self.notification_repo.delete(notification)
