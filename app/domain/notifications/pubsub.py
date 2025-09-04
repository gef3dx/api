import json
import logging
from typing import Dict, Any, Callable, Awaitable
import asyncio

import redis.asyncio as aioredis
import redis

from app.core.redis import get_async_redis, get_sync_redis
from app.domain.notifications.schemas import NotificationCreate

logger = logging.getLogger(__name__)


class NotificationPubSub:
    """Redis Pub/Sub system for distributed notifications."""

    def __init__(self):
        """Initialize the Pub/Sub system."""
        self.redis_client = get_async_redis()
        self.pubsub = self.redis_client.pubsub()
        self._listeners = {}

    async def publish_notification(self, notification: NotificationCreate) -> None:
        """
        Publish a notification to Redis Pub/Sub.

        Args:
            notification: The notification to publish
        """
        try:
            channel = f"notifications:user:{notification.user_id}"
            message = {
                "notification_id": (
                    str(notification.id) if hasattr(notification, "id") else None
                ),
                "user_id": str(notification.user_id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "priority": (
                    notification.priority.value
                    if hasattr(notification, "priority")
                    else "normal"
                ),
                "created_at": (
                    notification.created_at.isoformat()
                    if hasattr(notification, "created_at")
                    else None
                ),
            }

            await self.redis_client.publish(channel, json.dumps(message))
            logger.info(f"Published notification to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")

    def publish_notification_sync(self, notification: NotificationCreate) -> None:
        """
        Publish a notification to Redis Pub/Sub synchronously.

        Args:
            notification: The notification to publish
        """
        try:
            channel = f"notifications:user:{notification.user_id}"
            message = {
                "notification_id": (
                    str(notification.id) if hasattr(notification, "id") else None
                ),
                "user_id": str(notification.user_id),
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "priority": (
                    notification.priority.value
                    if hasattr(notification, "priority")
                    else "normal"
                ),
                "created_at": (
                    notification.created_at.isoformat()
                    if hasattr(notification, "created_at")
                    else None
                ),
            }

            # Use synchronous Redis client
            sync_redis = get_sync_redis()
            sync_redis.publish(channel, json.dumps(message))
            sync_redis.close()
            logger.info(f"Published notification to {channel}")
        except Exception as e:
            logger.error(f"Failed to publish notification: {e}")

    async def subscribe_to_user_notifications(
        self, user_id: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]
    ) -> None:
        """
        Subscribe to notifications for a specific user.

        Args:
            user_id: The user ID to subscribe to
            callback: Async callback function to handle notifications
        """
        channel = f"notifications:user:{user_id}"

        # Subscribe to the channel
        await self.pubsub.subscribe(channel)

        # Store the callback
        self._listeners[channel] = callback

        logger.info(f"Subscribed to notifications for user {user_id}")

    async def listen_for_notifications(self) -> None:
        """Listen for incoming notifications and process them with registered callbacks."""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])

                    # Process with registered callback
                    if channel in self._listeners:
                        try:
                            await self._listeners[channel](data)
                        except Exception as e:
                            logger.error(
                                f"Error processing notification for {channel}: {e}"
                            )
        except Exception as e:
            logger.error(f"Error listening for notifications: {e}")

    async def unsubscribe_from_user_notifications(self, user_id: str) -> None:
        """
        Unsubscribe from notifications for a specific user.

        Args:
            user_id: The user ID to unsubscribe from
        """
        channel = f"notifications:user:{user_id}"

        # Unsubscribe from the channel
        await self.pubsub.unsubscribe(channel)

        # Remove the callback
        if channel in self._listeners:
            del self._listeners[channel]

        logger.info(f"Unsubscribed from notifications for user {user_id}")

    async def close(self) -> None:
        """Close the Pub/Sub connection."""
        try:
            await self.pubsub.close()
            await self.redis_client.close()
        except Exception as e:
            logger.error(f"Error closing Pub/Sub connection: {e}")


# Global Pub/Sub instance
notification_pubsub = NotificationPubSub()