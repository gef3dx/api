from typing import Dict, Any, List, cast
from uuid import UUID
import logging

from app.core.celery_app import celery_app
from app.domain.messages.schemas import MessageCreate
from app.domain.messages.service import MessageService
from app.db.session import get_sync_db
from app.domain.messages.repository import MessageRepository
from app.domain.users.repository import UserRepository
# Import dependencies directly to avoid circular imports

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="messages")
def send_message_task(self, sender_id: str, message_data: Dict[str, Any]) -> str:
    """
    Celery task to send a message asynchronously.

    Args:
        sender_id: ID of the user sending the message
        message_data: Dictionary containing message data

    Returns:
        str: Message ID
    """
    try:
        # Convert dict to MessageCreate schema
        message_create = MessageCreate(**message_data)

        # Create service directly with sync session
        db = get_sync_db()
        message_repo = MessageRepository(db)
        user_repo = UserRepository(db)
        message_service = MessageService(message_repo, user_repo)

        # Send message
        message = message_service.send_message_sync(UUID(sender_id), message_create)

        logger.info(f"Message sent successfully: {message.id}")
        return str(message.id)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, queue="messages")
def process_message_batch_task(self, sender_id: str, message_batch: list) -> dict:
    """
    Celery task to process a batch of messages.

    Args:
        sender_id: ID of the user sending the messages
        message_batch: List of message data dictionaries

    Returns:
        dict: Processing results
    """
    try:
        results: Dict[str, Any] = {"success": 0, "failed": 0, "failed_messages": []}

        # Create service directly with sync session
        db = get_sync_db()
        message_repo = MessageRepository(db)
        user_repo = UserRepository(db)
        message_service = MessageService(message_repo, user_repo)

        for message_data in message_batch:
            try:
                # Convert dict to MessageCreate schema
                message_create = MessageCreate(**message_data)

                # Send message
                message_service.send_message_sync(UUID(sender_id), message_create)
                results["success"] = results["success"] + 1
            except Exception as e:
                results["failed"] = results["failed"] + 1
                cast(List, results["failed_messages"]).append(
                    {"data": message_data, "error": str(e)}
                )
                logger.error(f"Failed to process message in batch: {e}")

        logger.info(f"Batch processing completed: {results}")
        return results
    except Exception as e:
        logger.error(f"Failed to process message batch: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)