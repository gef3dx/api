import logging
from typing import Any, Dict, List, cast

from app.core.celery_app import celery_app
from app.db.session import get_sync_db
from app.domain.notifications.repository import NotificationRepository
from app.domain.notifications.schemas import NotificationCreate
from app.domain.notifications.service import NotificationService
from app.domain.users.repository import UserRepository

# Import dependencies directly to avoid circular imports

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="notifications")
def send_notification_task(self, notification_data: Dict[str, Any]) -> str:
    """
    Celery task to send a notification asynchronously.

    Args:
        notification_data: Dictionary containing notification data

    Returns:
        str: Notification ID
    """
    try:
        # Convert dict to NotificationCreate schema
        notification_create = NotificationCreate(**notification_data)

        # Create service directly with sync session
        db = get_sync_db()
        notification_repo = NotificationRepository(db)
        user_repo = UserRepository(db)
        notification_service = NotificationService(notification_repo, user_repo)

        # Send notification
        notification = notification_service.send_notification_sync(notification_create)

        logger.info(f"Notification sent successfully: {notification.id}")
        return str(notification.id)
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3) from e


@celery_app.task(bind=True, queue="notifications")
def process_notification_batch_task(self, notification_batch: list) -> dict:
    """
    Celery task to process a batch of notifications.

    Args:
        notification_batch: List of notification data dictionaries

    Returns:
        dict: Processing results
    """
    try:
        results: Dict[str, Any] = {
            "success": 0,
            "failed": 0,
            "failed_notifications": [],
        }

        # Create service directly with sync session
        db = get_sync_db()
        notification_repo = NotificationRepository(db)
        user_repo = UserRepository(db)
        notification_service = NotificationService(notification_repo, user_repo)

        for notification_data in notification_batch:
            try:
                # Convert dict to NotificationCreate schema
                notification_create = NotificationCreate(**notification_data)

                # Send notification
                notification_service.send_notification_sync(notification_create)
                results["success"] = results["success"] + 1
            except Exception as e:
                results["failed"] = results["failed"] + 1
                cast(List, results["failed_notifications"]).append(
                    {"data": notification_data, "error": str(e)}
                )
                logger.error(f"Failed to process notification in batch: {e}")

        logger.info(f"Batch processing completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Failed to process notification batch: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3) from e


@celery_app.task(bind=True, queue="notifications")
def cleanup_old_notifications_task(self, days_old: int = 30) -> int:
    """
    Celery task to clean up old notifications.

    Args:
        days_old: Number of days old to delete notifications

    Returns:
        int: Number of deleted notifications
    """
    try:
        # Create service directly with sync session
        # db = get_sync_db()
        # notification_repo = NotificationRepository(db)
        # user_repo = UserRepository(db)
        # notification_service = NotificationService(notification_repo, user_repo)

        # This would require implementing a cleanup method in the service
        # For now, we'll just log the task
        logger.info(f"Cleaning up notifications older than {days_old} days")
        deleted_count = 0  # Placeholder

        return deleted_count
    except Exception as e:
        logger.error(f"Failed to cleanup old notifications: {e}")
        raise self.retry(exc=e, countdown=300, max_retries=3) from e
