import uuid
from datetime import datetime
from typing import List, Optional, Union, cast, TYPE_CHECKING

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result as SyncResult

from app.domain.notifications.models import Notification, NotificationStatus
from app.domain.notifications.schemas import NotificationCreate

if TYPE_CHECKING:
    from sqlalchemy.engine import Result


class NotificationRepository:
    """
    Repository for handling notification database operations.
    """

    def __init__(self, db: Union[AsyncSession, Session]):
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
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(notification)
        else:
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def create_sync(self, notification_data: NotificationCreate) -> Notification:
        """
        Create a new notification synchronously.

        Args:
            notification_data: Notification creation data

        Returns:
            Notification: The created notification
        """
        notification_dict = notification_data.model_dump()
        notification = Notification(**notification_dict)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
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
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(query)
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_id_sync(self, notification_id: uuid.UUID) -> Optional[Notification]:
        """
        Get a notification by ID synchronously.

        Args:
            notification_id: The notification ID

        Returns:
            Notification or None: The notification if found, None otherwise
        """
        query = select(Notification).where(Notification.id == notification_id)
        result = self.db.execute(query)
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
            query = query.where(Notification.status == status)

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(query)
            scalars = result.scalars().all()
            return list(scalars)
        else:
            result = self.db.execute(query)
            return list(cast(SyncResult, result).scalars().all())

    def get_user_notifications_sync(
        self,
        user_id: uuid.UUID,
        status: Optional[NotificationStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Notification]:
        """
        Get notifications for a specific user synchronously.

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
            query = query.where(Notification.status == status)

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        result = self.db.execute(query)
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
            (Notification.user_id == user_id) & (Notification.status == NotificationStatus.UNREAD)
        )
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(query)
            scalars = result.scalars().all()
            return len(scalars)
        else:
            result = self.db.execute(query)
            return len(cast(SyncResult, result).scalars().all())

    def get_unread_count_sync(self, user_id: uuid.UUID) -> int:
        """
        Get the count of unread notifications for a user synchronously.

        Args:
            user_id: The user ID

        Returns:
            int: Count of unread notifications
        """
        query = select(Notification).where(
            (Notification.user_id == user_id) & (Notification.status == NotificationStatus.UNREAD)
        )
        result = self.db.execute(query)
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
                notification.read_at = datetime.utcnow()
            elif hasattr(notification, key):
                setattr(notification, key, value)
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(notification)
        else:
            self.db.commit()
            self.db.refresh(notification)
        return notification

    def update_sync(self, notification: Notification, **kwargs) -> Notification:
        """
        Update a notification synchronously.

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
                notification.read_at = datetime.utcnow()
            elif hasattr(notification, key):
                setattr(notification, key, value)
        self.db.commit()
        self.db.refresh(notification)
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
                read_at=datetime.utcnow()
            )
        )
        if isinstance(self.db, AsyncSession):
            await self.db.execute(stmt)
            await self.db.commit()
        else:
            self.db.execute(stmt)
            self.db.commit()

    def mark_as_read_sync(self, notification_ids: List[uuid.UUID]) -> None:
        """
        Mark multiple notifications as read synchronously.

        Args:
            notification_ids: List of notification IDs to mark as read
        """
        stmt = (
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .values(
                is_read=True,
                status=NotificationStatus.READ,
                read_at=datetime.utcnow()
            )
        )
        self.db.execute(stmt)
        self.db.commit()

    async def delete(self, notification: Notification) -> None:
        """
        Delete a notification.

        Args:
            notification: The notification to delete
        """
        if isinstance(self.db, AsyncSession):
            await self.db.delete(notification)
            await self.db.commit()
        else:
            self.db.delete(notification)
            self.db.commit()

    def delete_sync(self, notification: Notification) -> None:
        """
        Delete a notification synchronously.

        Args:
            notification: The notification to delete
        """
        self.db.delete(notification)
        self.db.commit()

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

    def delete_by_id_sync(self, notification_id: uuid.UUID) -> bool:
        """
        Delete a notification by ID synchronously.

        Args:
            notification_id: The notification ID

        Returns:
            bool: True if deleted, False if not found
        """
        notification = self.get_by_id_sync(notification_id)
        if notification:
            self.delete_sync(notification)
            return True
        return False