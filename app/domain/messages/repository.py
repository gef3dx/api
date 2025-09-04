import uuid
from typing import List, Optional, Union, cast, TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result as SyncResult

from app.domain.messages.models import Message
from app.domain.messages.schemas import MessageCreate

if TYPE_CHECKING:
    from sqlalchemy.engine import Result


class MessageRepository:
    """Repository for message-related database operations."""

    def __init__(self, db: Union[AsyncSession, Session]):
        self.db = db

    async def create(
        self, sender_id: uuid.UUID, message_create: MessageCreate
    ) -> Message:
        """
        Create a new message.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema

        Returns:
            Message: The created message
        """
        db_message = Message(
            sender_id=sender_id,
            recipient_id=message_create.recipient_id,
            subject=message_create.subject,
            content=message_create.content,
        )
        self.db.add(db_message)
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(db_message)
        else:
            self.db.commit()
            self.db.refresh(db_message)
        return db_message

    def create_sync(
        self, sender_id: uuid.UUID, message_create: MessageCreate
    ) -> Message:
        """
        Create a new message synchronously.

        Args:
            sender_id: The ID of the user sending the message
            message_create: Message creation schema

        Returns:
            Message: The created message
        """
        db_message = Message(
            sender_id=sender_id,
            recipient_id=message_create.recipient_id,
            subject=message_create.subject,
            content=message_create.content,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message

    async def get_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """
        Get a message by ID.

        Args:
            message_id: The message ID

        Returns:
            Message: The message or None if not found
        """
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(select(Message).where(Message.id == message_id))
            return result.scalar_one_or_none()
        else:
            result = self.db.execute(select(Message).where(Message.id == message_id))
            return cast(SyncResult, result).scalar_one_or_none()

    def get_by_id_sync(self, message_id: uuid.UUID) -> Optional[Message]:
        """
        Get a message by ID synchronously.

        Args:
            message_id: The message ID

        Returns:
            Message: The message or None if not found
        """
        result = self.db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

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
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(
                select(Message)
                .where((Message.sender_id == user_id) | (Message.recipient_id == user_id))
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            scalars = result.scalars().all()
            return list(scalars)
        else:
            result = self.db.execute(
                select(Message)
                .where((Message.sender_id == user_id) | (Message.recipient_id == user_id))
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(cast(SyncResult, result).scalars().all())

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
        result = self.db.execute(
            select(Message)
            .where((Message.sender_id == user_id) | (Message.recipient_id == user_id))
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(
                select(Message)
                .where(Message.recipient_id == user_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            scalars = result.scalars().all()
            return list(scalars)
        else:
            result = self.db.execute(
                select(Message)
                .where(Message.recipient_id == user_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(cast(SyncResult, result).scalars().all())

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
        result = self.db.execute(
            select(Message)
            .where(Message.recipient_id == user_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

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
        if isinstance(self.db, AsyncSession):
            result = await self.db.execute(
                select(Message)
                .where(Message.sender_id == user_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            scalars = result.scalars().all()
            return list(scalars)
        else:
            result = self.db.execute(
                select(Message)
                .where(Message.sender_id == user_id)
                .order_by(Message.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            return list(cast(SyncResult, result).scalars().all())

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
        result = self.db.execute(
            select(Message)
            .where(Message.sender_id == user_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, message: Message, **kwargs) -> Message:
        """
        Update a message.

        Args:
            message: The message to update
            **kwargs: Fields to update

        Returns:
            Message: The updated message
        """
        for key, value in kwargs.items():
            setattr(message, key, value)
        if isinstance(self.db, AsyncSession):
            await self.db.commit()
            await self.db.refresh(message)
        else:
            self.db.commit()
            self.db.refresh(message)
        return message

    def update_sync(self, message: Message, **kwargs) -> Message:
        """
        Update a message synchronously.

        Args:
            message: The message to update
            **kwargs: Fields to update

        Returns:
            Message: The updated message
        """
        for key, value in kwargs.items():
            setattr(message, key, value)
        self.db.commit()
        self.db.refresh(message)
        return message

    async def delete(self, message: Message) -> None:
        """
        Delete a message.

        Args:
            message: The message to delete
        """
        if isinstance(self.db, AsyncSession):
            await self.db.delete(message)
            await self.db.commit()
        else:
            self.db.delete(message)
            self.db.commit()

    def delete_sync(self, message: Message) -> None:
        """
        Delete a message synchronously.

        Args:
            message: The message to delete
        """
        self.db.delete(message)
        self.db.commit()