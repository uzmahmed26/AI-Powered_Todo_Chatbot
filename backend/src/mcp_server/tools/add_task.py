"""
add_task MCP Tool Implementation

Creates a new task in the database with user isolation.

This tool:
- Validates input (title 1-200 chars, user_id required)
- Creates Task record in database
- Returns structured success/error response
- Enforces user isolation via user_id
"""

from typing import Dict, Any
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import AddTaskInput, AddTaskOutput, TaskData, MCPErrorResponse

logger = logging.getLogger(__name__)


async def execute(user_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """
    Execute add_task MCP tool.

    Creates a new task for the specified user with the given title and
    optional description.

    Args:
        user_id: User ID from Better Auth (required for user isolation)
        title: Task title (1-200 characters)
        description: Optional task description

    Returns:
        Dictionary with success status, task data, and message

    Example:
        result = await execute(
            user_id="auth0|abc123",
            title="Buy groceries",
            description="Milk, bread, eggs"
        )
        # Returns: {
        #     "success": True,
        #     "data": {
        #         "task_id": 1,
        #         "title": "Buy groceries",
        #         "description": "Milk, bread, eggs",
        #         "status": "pending",
        #         "created_at": "2025-12-18T10:30:00Z"
        #     },
        #     "message": "Task created successfully"
        # }
    """
    try:
        # Validate input using Pydantic schema
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description,
        )

        logger.info(f"Creating task for user {user_id}: '{title}'")

        # Create database session
        async with async_session_maker() as session:
            # Create new task
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
            )

            # Add to database
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            logger.info(f"Task created successfully: task_id={new_task.id}")

            # Build response data - manually convert datetime to ISO strings
            result = {
                "success": True,
                "data": {
                    "task_id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "status": "pending" if not new_task.completed else "completed",
                    "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
                    "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None,
                },
                "message": "Task created successfully",
            }

            return result

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in add_task: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error creating task: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to create task. Please try again.",
            "error_code": "SERVER_ERROR",
        }
