"""
Conversation service for managing chat conversations.

Provides stateless conversation management:
- Create new conversations
- Retrieve conversations by ID
- Validate conversation ownership (user isolation)
"""

from typing import Optional
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException

from ...models.conversation import Conversation

logger = logging.getLogger(__name__)


async def create_conversation(session: AsyncSession, user_id: str) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        session: Database session
        user_id: User ID from Better Auth

    Returns:
        Created Conversation instance

    Raises:
        Exception: If database operation fails
    """
    try:
        logger.info(f"Creating new conversation for user: {user_id}")

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Conversation created: id={conversation.id}, user={user_id}")
        return conversation

    except Exception as e:
        logger.error(f"Error creating conversation: {e}", exc_info=True)
        await session.rollback()
        raise


async def get_conversation(
    session: AsyncSession, conversation_id: int, user_id: str
) -> Optional[Conversation]:
    """
    Retrieve a conversation by ID with ownership validation.

    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: User ID from Better Auth (for ownership validation)

    Returns:
        Conversation instance or None if not found

    Raises:
        HTTPException: If conversation exists but belongs to different user (403)
    """
    try:
        logger.info(f"Fetching conversation: id={conversation_id}, user={user_id}")

        statement = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation is None:
            logger.warning(f"Conversation not found: id={conversation_id}")
            return None

        # Validate ownership (user isolation)
        if conversation.user_id != user_id:
            logger.warning(
                f"Conversation ownership mismatch: "
                f"conversation.user_id={conversation.user_id}, "
                f"requested_user_id={user_id}"
            )
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this conversation",
            )

        logger.info(f"Conversation retrieved successfully: id={conversation_id}")
        return conversation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}", exc_info=True)
        raise


async def get_or_create_conversation(
    session: AsyncSession, user_id: str, conversation_id: Optional[int] = None
) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        session: Database session
        user_id: User ID from Better Auth
        conversation_id: Optional conversation ID

    Returns:
        Conversation instance (existing or new)

    Raises:
        HTTPException: If conversation_id provided but invalid/unauthorized
    """
    if conversation_id:
        # Try to get existing conversation
        conversation = await get_conversation(session, conversation_id, user_id)
        if conversation:
            return conversation

        # Conversation not found - create new one
        logger.info(
            f"Conversation {conversation_id} not found, creating new conversation"
        )

    # Create new conversation
    return await create_conversation(session, user_id)
