import uuid
from typing import List

from app.domain.messages.models import Message
from app.domain.messages.repository import MessageRepository
from app.domain.messages.schemas import MessageCreate, MessageUpdate
from app.domain.users.repository import UserRepository
from app.utils.exceptions import NotFoundException


class MessageService:
    """Service for message-related business logic."""

    def __init__(self, message_repo: MessageRepository, user_repo: UserRepository):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def send_message(
        self, sender_id: uuid.UUID, message_create: MessageCreate, sync: bool = False
    ) -> Message:
        """
        Send a new message.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema
            sync: If True, process synchronously; if False, queue for async processing

        Returns:
            Message: The created message

        Raises:
            NotFoundException: If recipient user not found
        """
        # Check if recipient exists
        recipient = await self.user_repo.get_by_id(message_create.recipient_id)
        if not recipient:
            raise NotFoundException(
                "Recipient user not found",
                {"recipient_id": str(message_create.recipient_id)},
            )

        # For sync requests, process immediately
        if sync:
            # Create message immediately
            return await self.message_repo.create(sender_id, message_create)
        else:
            # For async processing, we'll create the message immediately but
            # in a full implementation, you might want to mark it as pending
            # and update it when the async task completes
            return await self.message_repo.create(sender_id, message_create)

    def send_message_sync(
        self, sender_id: uuid.UUID, message_create: MessageCreate
    ) -> Message:
        """
        Send a new message synchronously for use in Celery tasks.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema

        Returns:
            Message: The created message

        Raises:
            NotFoundException: If recipient user not found
        """
        # Check if recipient exists
        recipient = self.user_repo.get_by_id_sync(message_create.recipient_id)
        if not recipient:
            raise NotFoundException(
                "Recipient user not found",
                {"recipient_id": str(message_create.recipient_id)},
            )

        # Create message immediately
        return self.message_repo.create_sync(sender_id, message_create)

    async def get_message_by_id(self, message_id: uuid.UUID) -> Message:
        """
        Get a message by ID.

        Args:
            message_id: The message ID

        Returns:
            Message: The message

        Raises:
            NotFoundException: If message not found
        """
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            raise NotFoundException(
                "Message not found", {"message_id": str(message_id)}
            )
        return message

    def get_message_by_id_sync(self, message_id: uuid.UUID) -> Message:
        """
        Get a message by ID synchronously.

        Args:
            message_id: The message ID

        Returns:
            Message: The message

        Raises:
            NotFoundException: If message not found
        """
        message = self.message_repo.get_by_id_sync(message_id)
        if not message:
            raise NotFoundException(
                "Message not found", {"message_id": str(message_id)}
            )
        return message

    async def get_user_messages(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a user (sent or received).

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of messages
        """
        return await self.message_repo.get_user_messages(user_id, skip, limit)

    def get_user_messages_sync(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a user (sent or received) synchronously.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of messages
        """
        return self.message_repo.get_user_messages_sync(user_id, skip, limit)

    async def get_user_inbox(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages received by a user.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of received messages
        """
        return await self.message_repo.get_user_inbox(user_id, skip, limit)

    def get_user_inbox_sync(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages received by a user synchronously.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of received messages
        """
        return self.message_repo.get_user_inbox_sync(user_id, skip, limit)

    async def get_user_sent_messages(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages sent by a user.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of sent messages
        """
        return await self.message_repo.get_user_sent_messages(user_id, skip, limit)

    def get_user_sent_messages_sync(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get messages sent by a user synchronously.

        Args:
            user_id: The user ID
            skip: Number of messages to skip
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of sent messages
        """
        return self.message_repo.get_user_sent_messages_sync(user_id, skip, limit)

    async def update_message(
        self, message_id: uuid.UUID, message_update: MessageUpdate
    ) -> Message:
        """
        Update a message.

        Args:
            message_id: The message ID
            message_update: Message update schema

        Returns:
            Message: The updated message

        Raises:
            NotFoundException: If message not found
        """
        message = await self.get_message_by_id(message_id)
        update_data = message_update.dict(exclude_unset=True)
        return await self.message_repo.update(message, **update_data)

    def update_message_sync(
        self, message_id: uuid.UUID, message_update: MessageUpdate
    ) -> Message:
        """
        Update a message synchronously.

        Args:
            message_id: The message ID
            message_update: Message update schema

        Returns:
            Message: The updated message

        Raises:
            NotFoundException: If message not found
        """
        message = self.get_message_by_id_sync(message_id)
        update_data = message_update.dict(exclude_unset=True)
        return self.message_repo.update_sync(message, **update_data)

    async def delete_message(self, message_id: uuid.UUID) -> None:
        """
        Delete a message.

        Args:
            message_id: The message ID

        Raises:
            NotFoundException: If message not found
        """
        message = await self.get_message_by_id(message_id)
        await self.message_repo.delete(message)

    def delete_message_sync(self, message_id: uuid.UUID) -> None:
        """
        Delete a message synchronously.

        Args:
            message_id: The message ID

        Raises:
            NotFoundException: If message not found
        """
        message = self.get_message_by_id_sync(message_id)
        self.message_repo.delete_sync(message)
