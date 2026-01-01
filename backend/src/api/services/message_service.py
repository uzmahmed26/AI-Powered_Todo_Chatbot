"""
Message service for managing chat messages.

Provides stateless message management:
- Store user and assistant messages
- Load conversation history
- Support pagination for long conversations
"""

from typing import List, Dict, Any
import logging
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.message import Message, MessageRole

logger = logging.getLogger(__name__)


async def store_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    role: MessageRole,
    content: str,
    detected_language: str = "en",
) -> Message:
    """
    Store a message in the database.

    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: User ID from Better Auth
        role: Message role (user or assistant)
        content: Message content
        detected_language: Detected language code (en or ur, default: en)

    Returns:
        Created Message instance

    Raises:
        Exception: If database operation fails
    """
    try:
        logger.info(
            f"Storing message: conversation={conversation_id}, "
            f"role={role}, user={user_id}, language={detected_language}"
        )

        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            detected_language=detected_language,
        )

        session.add(message)
        await session.commit()
        await session.refresh(message)

        logger.info(f"Message stored: id={message.id}")
        return message

    except Exception as e:
        logger.error(f"Error storing message: {e}", exc_info=True)
        await session.rollback()
        raise


async def load_conversation_history(
    session: AsyncSession,
    conversation_id: int,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict[str, str]]:
    """
    Load conversation history from database.

    Returns messages in chronological order (oldest first) for AI agent context.
    Supports pagination for long conversations.

    Args:
        session: Database session
        conversation_id: Conversation ID
        limit: Maximum number of messages to load (default: 20)
        offset: Offset for pagination (default: 0)

    Returns:
        List of message dictionaries with role and content

    Example:
        [
            {"role": "user", "content": "Add buy milk"},
            {"role": "assistant", "content": "✓ Added 'buy milk'"}
        ]
    """
    try:
        logger.info(
            f"Loading conversation history: id={conversation_id}, "
            f"limit={limit}, offset={offset}"
        )

        # Query messages for this conversation, ordered by creation time
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)  # Chronological order
            .offset(offset)
            .limit(limit)
        )

        result = await session.execute(statement)
        messages = result.scalars().all()

        # Convert to OpenAI format
        history = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

        logger.info(f"Loaded {len(history)} messages from conversation {conversation_id}")
        return history

    except Exception as e:
        logger.error(f"Error loading conversation history: {e}", exc_info=True)
        raise


async def get_recent_messages(
    session: AsyncSession,
    conversation_id: int,
    count: int = 20,
) -> List[Dict[str, str]]:
    """
    Get the most recent messages from a conversation.

    Useful for providing AI agent context without loading entire history.

    Args:
        session: Database session
        conversation_id: Conversation ID
        count: Number of recent messages to retrieve

    Returns:
        List of recent message dictionaries (chronological order)
    """
    try:
        logger.info(f"Getting {count} recent messages from conversation {conversation_id}")

        # Get recent messages (DESC order for recency, then reverse)
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(count)
        )

        result = await session.execute(statement)
        messages = list(result.scalars().all())

        # Reverse to chronological order (oldest to newest)
        messages.reverse()

        # Convert to OpenAI format
        history = [
            {"role": msg.role.value, "content": msg.content} for msg in messages
        ]

        logger.info(f"Retrieved {len(history)} recent messages")
        return history

    except Exception as e:
        logger.error(f"Error getting recent messages: {e}", exc_info=True)
        raise
