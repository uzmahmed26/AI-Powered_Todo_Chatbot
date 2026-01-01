"""
Chat endpoint for Phase III Smart Todo ChatKit App.

Provides the stateless chat endpoint:
- POST /api/{user_id}/chat: Process chat messages

This endpoint is completely stateless - all conversation state
is loaded from the database on each request.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel.ext.asyncio.session import AsyncSession
import logging

from ...database.engine import get_async_session
from ...models.user import User
from ...auth.dependencies import get_current_active_user
from ..models import ChatRequest, ChatResponse, ToolCall
from ..services.chat_service import process_chat_message

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=200,
    summary="Process chat message",
    description=(
        "Process a chat message for a user. "
        "This endpoint is stateless - all conversation state is "
        "loaded from the database on each request. "
        "Supports both new and existing conversations."
    ),
    responses={
        200: {
            "description": "Chat message processed successfully",
            "model": ChatResponse,
        },
        400: {"description": "Bad Request - Invalid input"},
        403: {"description": "Forbidden - Invalid conversation access"},
        500: {"description": "Internal Server Error"},
        503: {"description": "Service Unavailable - OpenAI API or database unavailable"},
        504: {"description": "Gateway Timeout - Request took too long"},
    },
)
async def process_chat(
    user_id: str = Path(
        ...,
        description="User ID from JWT authentication",
        example="uuid-string",
    ),
    request: ChatRequest = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
) -> ChatResponse:
    """
    Process a chat message and return AI agent response.

    Flow:
    1. Validates user_id and request
    2. Loads conversation history from database (if conversation_id provided)
    3. Stores user message
    4. Invokes AI agent with MCP tools
    5. Stores assistant message
    6. Returns response with conversation_id

    Stateless Architecture:
    - No in-memory conversation state
    - All data loaded from database per request
    - Horizontal scaling ready

    Args:
        user_id: User ID from Better Auth (path parameter)
        request: Chat request with message and optional conversation_id
        session: Database session (injected)

    Returns:
        ChatResponse with conversation_id, agent response, and tool calls

    Raises:
        HTTPException: Various HTTP errors (400, 403, 500, 503, 504)

    Example Request:
        POST /api/auth0|abc123/chat
        {
            "message": "Add buy milk to my tasks",
            "conversation_id": null
        }

    Example Response:
        {
            "conversation_id": 1,
            "response": "✓ Added 'buy milk' to your tasks (Task #1)",
            "tool_calls": [
                {
                    "tool": "add_task",
                    "args": {"user_id": "auth0|abc123", "title": "buy milk"},
                    "result": {"success": true, "data": {"task_id": 1}}
                }
            ],
            "success": true
        }
    """
    try:
        # Verify user_id matches authenticated user
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot access other user's conversations",
            )

        logger.info(
            f"Chat endpoint called: user_id={user_id}, "
            f"conversation_id={request.conversation_id}"
        )

        # Process chat message through service
        result = await process_chat_message(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id,
            detected_language=request.detected_language,
        )

        # Convert tool calls to response model
        tool_calls = [
            ToolCall(
                tool=tc["tool"],
                args=tc["args"],
                result=tc["result"],
            )
            for tc in result.get("tool_calls", [])
        ]

        # Build response
        response = ChatResponse(
            conversation_id=result["conversation_id"],
            response=result["response"],
            tool_calls=tool_calls,
            success=result["success"],
        )

        logger.info(f"Chat request successful: conversation_id={response.conversation_id}")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions (403, etc.)
        raise

    except ValueError as e:
        # Validation errors
        logger.warning(f"Validation error in chat endpoint: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}",
        )

    except Exception as e:
        # Unexpected errors
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)

        # Check if it's an OpenAI API error
        if "openai" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="AI service is currently unavailable. Please try again later.",
            )

        # Check if it's a database error
        if "database" in str(e).lower() or "connection" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Database service is currently unavailable. Please try again later.",
            )

        # Generic server error
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred. Please try again.",
        )
