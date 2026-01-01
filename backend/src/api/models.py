"""
Pydantic models for API request/response schemas.

Defines the data models for the stateless chat endpoint:
- ChatRequest: Incoming chat messages
- ChatResponse: Agent responses with conversation data
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    Request model for POST /api/{user_id}/chat endpoint.

    Attributes:
        message: User's chat message (required)
        conversation_id: Optional conversation ID for resuming
        detected_language: Optional detected language code (en or ur)
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's chat message",
        examples=["Add buy milk to my tasks"],
    )
    conversation_id: Optional[int] = Field(
        None,
        gt=0,
        description="Conversation ID for resuming existing conversation",
        examples=[123],
    )
    detected_language: Optional[str] = Field(
        "en",
        pattern="^(en|ur)$",
        description="Detected language code (en for English, ur for Urdu)",
        examples=["en", "ur"],
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "message": "Remind me to buy groceries tomorrow",
                "conversation_id": 42,
                "detected_language": "en",
            }
        }


class ToolCall(BaseModel):
    """
    Model for tool call information.

    Attributes:
        tool: Tool name (e.g., "add_task")
        args: Tool arguments
        result: Tool execution result
    """

    tool: str = Field(..., description="Tool name")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    result: Dict[str, Any] = Field(..., description="Tool execution result")


class ChatResponse(BaseModel):
    """
    Response model for POST /api/{user_id}/chat endpoint.

    Attributes:
        conversation_id: Conversation ID (new or existing)
        response: Agent's text response
        tool_calls: List of tools invoked during processing
        success: Whether processing succeeded
    """

    conversation_id: int = Field(
        ...,
        description="Conversation ID for this chat session",
        examples=[123],
    )
    response: str = Field(
        ...,
        description="Agent's natural language response",
        examples=["✓ Added 'buy milk' to your tasks for tomorrow"],
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="List of tools invoked by the agent",
    )
    success: bool = Field(
        True,
        description="Whether the request was processed successfully",
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "conversation_id": 42,
                "response": "✓ Added 'buy milk' to your tasks",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "args": {"user_id": "auth0|abc", "title": "buy milk"},
                        "result": {"success": True, "data": {"task_id": 1}},
                    }
                ],
                "success": True,
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model for API errors.

    Attributes:
        error: Error message
        detail: Optional detailed error information
        status_code: HTTP status code
    """

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "error": "Bad Request",
                "detail": "Message field is required",
                "status_code": 400,
            }
        }
