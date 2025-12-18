"""
list_tasks MCP Tool Implementation

Lists tasks for a user with optional status filtering.

This tool:
- Validates input (user_id required, status filter optional)
- Queries Task records from database with user isolation
- Returns structured success/error response
- Enforces user isolation via user_id
- Provides friendly empty-state message
"""

from typing import Dict, Any
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import ListTasksInput, ListTasksOutput, TaskData, MCPErrorResponse

logger = logging.getLogger(__name__)


async def execute(user_id: str, status: str = "all") -> Dict[str, Any]:
    """
    Execute list_tasks MCP tool.

    Lists all tasks for the specified user, optionally filtered by status.

    Args:
        user_id: User ID from Better Auth (required for user isolation)
        status: Filter by status ("all", "pending", "completed"), defaults to "all"

    Returns:
        Dictionary with success status, list of tasks, and message

    Example:
        result = await execute(
            user_id="auth0|abc123",
            status="pending"
        )
        # Returns: {
        #     "success": True,
        #     "data": {
        #         "tasks": [
        #             {
        #                 "task_id": 1,
        #                 "title": "Buy groceries",
        #                 "description": "Milk, bread, eggs",
        #                 "status": "pending",
        #                 "created_at": "2025-12-18T10:30:00Z"
        #             }
        #         ],
        #         "count": 1
        #     },
        #     "message": "Found 1 task"
        # }
    """
    try:
        # Validate input using Pydantic schema
        input_data = ListTasksInput(
            user_id=user_id,
            status=status,
        )

        logger.info(f"Listing tasks for user {user_id} with status filter: {status}")

        # Create database session
        async with async_session_maker() as session:
            # Build query with user isolation
            query = select(Task).where(Task.user_id == input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                query = query.where(Task.completed == False)
            elif input_data.status == "completed":
                query = query.where(Task.completed == True)
            # "all" status doesn't need additional filtering

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Found {len(tasks)} tasks for user {user_id}")

            # Build response data
            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": "pending" if not task.completed else "completed",
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                })

            # Friendly empty-state message
            if len(tasks) == 0:
                message = "You don't have any tasks yet. Try creating one!"
            elif len(tasks) == 1:
                message = "Found 1 task"
            else:
                message = f"Found {len(tasks)} tasks"

            return {
                "success": True,
                "data": {
                    "tasks": task_list,
                    "count": len(tasks),
                },
                "message": message,
            }

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in list_tasks: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to retrieve tasks. Please try again.",
            "error_code": "SERVER_ERROR",
        }
