"""
update_task MCP Tool Implementation

Updates an existing task's fields.
"""

from typing import Dict, Any
from datetime import datetime
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import UpdateTaskInput, UpdateTaskOutput, TaskData, MCPErrorResponse

logger = logging.getLogger(__name__)


async def execute(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,
    category: str = None,
    due_date: str = None
) -> Dict[str, Any]:
    """
    Execute update_task MCP tool.

    Updates fields of an existing task.

    Args:
        user_id: User ID from JWT Auth (required for user isolation)
        task_id: Task ID to update
        title: New task title (optional)
        description: New task description (optional)
        priority: New task priority (optional)
        category: New task category (optional)
        due_date: New due date in ISO format (optional)

    Returns:
        Dictionary with success status, updated task data, and message
    """
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date is not None:
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
        input_data = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
        )

        logger.info(f"Updating task {task_id} for user {user_id}")

        # Create database session
        async with async_session_maker() as session:
            # Fetch task with user isolation
            query = select(Task).where(
                Task.id == input_data.task_id,
                Task.user_id == input_data.user_id
            )
            result = await session.execute(query)
            task = result.scalar_one_or_none()

            if not task:
                logger.warning(f"Task {task_id} not found for user {user_id}")
                return {
                    "success": False,
                    "data": None,
                    "message": f"Task #{task_id} not found or you don't have permission to update it",
                    "error_code": "NOT_FOUND",
                }

            # Update fields if provided
            if input_data.title is not None:
                task.title = input_data.title
            if input_data.description is not None:
                task.description = input_data.description
            if input_data.priority is not None:
                task.priority = input_data.priority
            if input_data.category is not None:
                task.category = input_data.category
            if due_date is not None:
                task.due_date = parsed_due_date

            # Save changes
            session.add(task)
            await session.commit()
            await session.refresh(task)

            logger.info(f"Task {task_id} updated successfully")

            # Build response data
            result = {
                "success": True,
                "data": {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": "pending" if not task.completed else "completed",
                    "priority": task.priority,
                    "category": task.category,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                },
                "message": "Task updated successfully",
            }

            return result

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in update_task: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error updating task: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to update task. Please try again.",
            "error_code": "SERVER_ERROR",
        }
