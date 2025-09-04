import asyncio
import logging
from app.domain.notifications.pubsub import notification_pubsub

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_notification(notification_data: dict):
    """
    Handle incoming notifications.

    Args:
        notification_data: Notification data from Redis Pub/Sub
    """
    logger.info(f"Received notification: {notification_data}")
    # In a real application, you might:
    # - Send push notifications to mobile devices
    # - Update WebSocket connections for real-time UI updates
    # - Trigger email notifications
    # - Log the notification for analytics


async def main():
    """Main function to demonstrate notification listening."""
    # Subscribe to notifications for a specific user
    user_id = "example-user-id"  # Replace with actual user ID
    await notification_pubsub.subscribe_to_user_notifications(
        user_id, handle_notification
    )

    # Start listening for notifications
    logger.info("Starting notification listener...")
    await notification_pubsub.listen_for_notifications()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopping notification listener...")
