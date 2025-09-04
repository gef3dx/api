import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.notifications.models import Notification, NotificationStatus
from app.domain.notifications.schemas import NotificationCreate


class NotificationRepository:
    """
    Repository for handling notification database operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification_data: NotificationCreate) -> Notification:
        """
        Create a new notification.

        Args:
            notification_data: Notification creation data

        Returns:
            Notification: The created notification
        """
        notification_dict = notification_data.model_dump()
        notification = Notification(**notification_dict)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: uuid.UUID) -> Optional[Notification]:
        """
        Get a notification by ID.

        Args:
            notification_id: The notification ID

        Returns:
            Notification or None: The notification if found, None otherwise
        """
        query = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        """
        Get notifications for a specific user.

        Args:
            user_id: The user ID
            status: Optional status filter
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return

        Returns:
            List[Notification]: List of notifications
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if status:
            query = query.where(Notification.status == status)  # type: ignore[arg-type]

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: The user ID

        Returns:
            int: Count of unread notifications
        """
        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.status == NotificationStatus.UNREAD,  # type: ignore[arg-type]
        )
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def update(self, notification: Notification, **kwargs) -> Notification:
        """
        Update a notification.

        Args:
            notification: The notification to update
            **kwargs: Fields to update

        Returns:
            Notification: The updated notification
        """
        for key, value in kwargs.items():
            if key == "is_read" and value is True:
                # If marking as read, also update status and read_at
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()  # type: ignore[assignment]
            elif hasattr(notification, key):
                setattr(notification, key, value)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def mark_as_read(self, notification_ids: List[uuid.UUID]) -> None:
        """
        Mark multiple notifications as read.

        Args:
            notification_ids: List of notification IDs to mark as read
        """
        stmt = (
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .values(
                is_read=True,
                status=NotificationStatus.READ,
                read_at=datetime.utcnow(),
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete(self, notification: Notification) -> None:
        """
        Delete a notification.

        Args:
            notification: The notification to delete
        """
        await self.db.delete(notification)
        await self.db.commit()

    async def delete_by_id(self, notification_id: uuid.UUID) -> bool:
        """
        Delete a notification by ID.

        Args:
            notification_id: The notification ID

        Returns:
            bool: True if deleted, False if not found
        """
        notification = await self.get_by_id(notification_id)
        if notification:
            await self.delete(notification)
            return True
        return False
