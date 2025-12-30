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


async def execute(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",
    category: str = None,
    due_date: str = None
) -> Dict[str, Any]:
    """
    Execute add_task MCP tool.

    Creates a new task for the specified user with title, description,
    priority, category, and optional due date.

    Args:
        user_id: User ID from JWT Auth (required for user isolation)
        title: Task title (1-200 characters)
        description: Optional task description
        priority: Task priority (high, medium, low) - defaults to medium
        category: Task category (work, home, study, etc.) - optional
        due_date: Due date in ISO format - optional

    Returns:
        Dictionary with success status, task data, and message

    Example:
        result = await execute(
            user_id="uuid-123",
            title="Buy groceries",
            description="Milk, bread, eggs",
            priority="high",
            category="shopping",
            due_date="2025-01-15T10:00:00Z"
        )
    """
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "data": None,
                    "message": "Invalid due_date format. Use ISO format (e.g., 2025-01-15T10:00:00Z)",
                    "error_code": "VALIDATION_ERROR",
                }

        # Validate input using Pydantic schema
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
        )

        logger.info(f"Creating task for user {user_id}: '{title}' (priority={priority}, category={category})")

        # Create database session
        async with async_session_maker() as session:
            # Create new task
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
                priority=input_data.priority,
                category=input_data.category,
                due_date=parsed_due_date,
            )

            # Add to database
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            logger.info(f"Task created successfully: task_id={new_task.id}")

            # Build response data
            result = {
                "success": True,
                "data": {
                    "task_id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "status": "pending" if not new_task.completed else "completed",
                    "priority": new_task.priority,
                    "category": new_task.category,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
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
