"""
Chatbot API Routes
============================================================================
Phase III: REST API endpoints for chatbot interactions
Integrates with OpenAI and manages conversation state
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.chatbot import TodoChatbot
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message"""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request from frontend"""
    message: str
    conversation_history: List[ChatMessage] = []
    use_tools: bool = True  # Whether to enable function calling


class ChatResponse(BaseModel):
    """Chat response to frontend"""
    message: str
    tool_calls: List[Dict[str, Any]] = []
    conversation_id: Optional[str] = None


# Chatbot instance (singleton)
_chatbot_instance = None


def get_chatbot() -> TodoChatbot:
    """Dependency to get chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = TodoChatbot()
    return _chatbot_instance


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    chatbot: TodoChatbot = Depends(get_chatbot)
):
    """
    Main chat endpoint

    Receives user message, processes with AI, returns response
    """
    try:
        # Convert conversation history to dict format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]

        # Get tools if enabled
        tools = chatbot.get_todo_tools() if request.use_tools else None

        # Process with AI
        response = await chatbot.chat(
            user_message=request.message,
            conversation_history=history,
            available_tools=tools
        )

        return ChatResponse(
            message=response["content"] or "",
            tool_calls=response.get("tool_calls", [])
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/health")
async def chatbot_health():
    """Health check for chatbot service"""
    return {
        "status": "healthy",
        "service": "chatbot",
        "openai_configured": bool(get_chatbot().api_key)
    }


# Tool execution endpoints
@router.post("/execute-tool")
async def execute_tool(
    tool_name: str,
    arguments: Dict[str, Any]
):
    """
    Execute a tool function called by the AI

    This endpoint receives tool calls from the AI and executes them
    Returns results that can be sent back to the AI for final response
    """
    try:
        # Import task service
        from ..services.tasks import TaskService
        task_service = TaskService()

        # Execute based on tool name
        if tool_name == "add_task":
            result = await task_service.create_task(
                title=arguments["title"],
                priority=arguments.get("priority", "medium"),
                due_date=arguments.get("due_date")
            )
            return {"success": True, "data": result}

        elif tool_name == "get_tasks":
            result = await task_service.get_tasks(
                status=arguments.get("status", "all"),
                priority=arguments.get("priority")
            )
            return {"success": True, "data": result}

        elif tool_name == "update_task":
            result = await task_service.update_task(
                task_id=arguments["task_id"],
                **{k: v for k, v in arguments.items() if k != "task_id"}
            )
            return {"success": True, "data": result}

        elif tool_name == "delete_task":
            result = await task_service.delete_task(
                task_id=arguments["task_id"]
            )
            return {"success": True, "data": result}

        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return {"success": False, "error": str(e)}
