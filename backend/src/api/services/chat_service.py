"""
Chat service for orchestrating the complete chat flow.

Coordinates the stateless chat process:
1. Load conversation history from database
2. Store user message
3. Invoke AI agent with MCP tools
4. Store assistant message
5. Return response

This service maintains the stateless architecture by loading all
conversation state from the database on each request.
"""

from typing import Dict, Any, Optional
import logging
from sqlmodel.ext.asyncio.session import AsyncSession

from ...agent.agent import TodoAgent
from ...models.message import MessageRole
from .conversation_service import get_or_create_conversation
from .message_service import store_message, get_recent_messages

logger = logging.getLogger(__name__)


async def process_chat_message(
    session: AsyncSession,
    user_id: str,
    message: str,
    conversation_id: Optional[int] = None,
    max_context_messages: int = 20,
    detected_language: Optional[str] = "en",
) -> Dict[str, Any]:
    """
    Process a chat message through the complete flow.

    This function orchestrates:
    1. Conversation retrieval/creation
    2. User message storage
    3. Conversation history loading
    4. AI agent processing (with MCP tools)
    5. Assistant message storage
    6. Response formatting

    Args:
        session: Database session
        user_id: User ID from Better Auth
        message: User's message text
        conversation_id: Optional conversation ID (None = new conversation)
        max_context_messages: Maximum messages to load for context (default: 20)
        detected_language: Detected language code (en or ur, default: en)

    Returns:
        Dictionary with:
            - conversation_id: Conversation ID
            - response: Agent's response text
            - tool_calls: List of tools invoked
            - success: Whether processing succeeded

    Raises:
        Exception: If any step fails

    Example:
        result = await process_chat_message(
            session=session,
            user_id="auth0|abc123",
            message="Add buy milk to my tasks",
            conversation_id=None,
            detected_language="en"
        )
        # Returns: {
        #     "conversation_id": 1,
        #     "response": "✓ Added 'buy milk' to your tasks",
        #     "tool_calls": [{...}],
        #     "success": True
        # }
    """
    try:
        logger.info(f"Processing chat message for user: {user_id}")

        # Step 1: Get or create conversation
        conversation = await get_or_create_conversation(
            session, user_id, conversation_id
        )
        logger.info(f"Using conversation: id={conversation.id}")

        # Step 2: Store user message
        await store_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.USER,
            content=message,
            detected_language=detected_language,
        )
        logger.info(f"User message stored with language: {detected_language}")

        # Step 3: Load conversation history for context
        conversation_history = await get_recent_messages(
            session=session,
            conversation_id=conversation.id,
            count=max_context_messages,
        )
        logger.info(f"Loaded {len(conversation_history)} messages for context")

        # Step 4: Initialize and run AI agent
        agent = TodoAgent(user_id=user_id, language=detected_language)
        agent_result = await agent.process_message(
            message=message,
            conversation_history=conversation_history[:-1],  # Exclude the message we just stored
        )
        logger.info(f"Agent processing complete: success={agent_result.get('success')}")

        # Step 5: Store assistant message
        assistant_response = agent_result.get("response", "")
        await store_message(
            session=session,
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=assistant_response,
            detected_language=detected_language,
        )
        logger.info(f"Assistant message stored with language: {detected_language}")

        # Step 6: Build final response
        response = {
            "conversation_id": conversation.id,
            "response": assistant_response,
            "tool_calls": agent_result.get("tool_calls", []),
            "success": agent_result.get("success", True),
        }

        logger.info(f"Chat message processing complete: conversation={conversation.id}")
        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        # Don't rollback session here - let the endpoint handle it
        raise
