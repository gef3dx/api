import asyncio
from uuid import UUID

from app.db.session import get_db
from app.domain.notifications.enums import NotificationPriority, NotificationType
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import NotificationCreate
from app.domain.notifications.service import NotificationService
from app.domain.users.repository import UserRepository


async def main():
    """Example of sending a notification with all new features."""

    # In a real application, you would get these from dependency injection
    async for db in get_db():
        notification_repo = NotificationRepository(db)
        user_repo = UserRepository(db)
        notification_service = NotificationService(notification_repo, user_repo)

        # Create a notification with priority
        notification_data = NotificationCreate(
            user_id=UUID(
                "00000000-0000-0000-0000-000000000000"
            ),  # Replace with actual user ID
            title="High Priority Alert",
            message="This is an urgent notification that requires immediate attention.",
            type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
        )

        # Send the notification (will be processed asynchronously)
        notification = await notification_service.send_notification(notification_data)
        print(f"Notification sent with ID: {notification.id}")

        break


if __name__ == "__main__":
    asyncio.run(main())
