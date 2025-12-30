"""
list_tasks MCP Tool Implementation

Lists tasks for a user with filtering, search, and sorting.
"""

from typing import Dict, Any
from datetime import datetime
import logging
from sqlmodel import select, or_, func, case
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import ListTasksInput, ListTasksOutput, TaskData, MCPErrorResponse
from ...utils.recurrence import calculate_next_due_date

logger = logging.getLogger(__name__)


async def execute(
    user_id: str,
    status: str = "all",
    priority: str = None,
    category: str = None,
    search: str = None,
    due_date_from: str = None,
    due_date_to: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Execute list_tasks MCP tool with advanced filtering.

    Args:
        user_id: User ID from JWT Auth
        status: Filter by status (all, pending, completed)
        priority: Filter by priority (high, medium, low)
        category: Filter by category
        search: Search keyword in title/description
        due_date_from: Filter tasks due from this date (ISO format)
        due_date_to: Filter tasks due until this date (ISO format)
        sort_by: Sort field (created_at, due_date, priority, title)
        sort_order: Sort order (asc, desc)

    Returns:
        Dictionary with success status, task list, and metadata
    """
    try:
        # Validate input
        input_data = ListTasksInput(
            user_id=user_id,
            status=status,
            priority=priority,
            category=category,
            search=search,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        logger.info(f"Listing tasks for user {user_id} (status={status}, priority={priority}, category={category})")

        # Create database session
        async with async_session_maker() as session:
            # Build query with user isolation
            query = select(Task).where(Task.user_id == input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                query = query.where(Task.completed == False)
            elif input_data.status == "completed":
                query = query.where(Task.completed == True)

            # Apply priority filter
            if input_data.priority:
                query = query.where(Task.priority == input_data.priority)

            # Apply category filter
            if input_data.category:
                query = query.where(Task.category == input_data.category)

            # Apply search (case-insensitive, partial match)
            if input_data.search:
                search_pattern = f"%{input_data.search}%"
                query = query.where(
                    or_(
                        Task.title.ilike(search_pattern),
                        Task.description.ilike(search_pattern)
                    )
                )

            # Apply due date filters
            if input_data.due_date_from:
                try:
                    date_from = datetime.fromisoformat(input_data.due_date_from.replace('Z', '+00:00'))
                    query = query.where(Task.due_date >= date_from)
                except ValueError:
                    pass

            if input_data.due_date_to:
                try:
                    date_to = datetime.fromisoformat(input_data.due_date_to.replace('Z', '+00:00'))
                    query = query.where(Task.due_date <= date_to)
                except ValueError:
                    pass

            # Apply sorting
            if input_data.sort_by == "due_date":
                # Sort with NULL values last
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.due_date.asc().nullslast())
                else:
                    query = query.order_by(Task.due_date.desc().nullslast())
            elif input_data.sort_by == "priority":
                # Custom priority order: high > medium > low
                priority_order = case(
                    (Task.priority == "high", 1),
                    (Task.priority == "medium", 2),
                    (Task.priority == "low", 3),
                    else_=4
                )
                if input_data.sort_order == "asc":
                    query = query.order_by(priority_order.asc())
                else:
                    query = query.order_by(priority_order.desc())
            elif input_data.sort_by == "title":
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.title.asc())
                else:
                    query = query.order_by(Task.title.desc())
            else:  # created_at (default)
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.created_at.asc())
                else:
                    query = query.order_by(Task.created_at.desc())

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Found {len(tasks)} tasks for user {user_id}")

            # Build response data
            task_list = []
            for task in tasks:
                # Calculate next recurrence date if task is recurring and not completed
                next_recurrence = None
                if task.is_recurring and task.recurrence_pattern and not task.completed:
                    try:
                        next_recurrence_date = calculate_next_due_date(
                            current_due_date=task.due_date,
                            recurrence_pattern=task.recurrence_pattern,
                            recurrence_interval=task.recurrence_interval,
                        )
                        next_recurrence = next_recurrence_date.isoformat()
                    except Exception as e:
                        logger.warning(f"Failed to calculate next recurrence for task {task.id}: {e}")

                task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": "pending" if not task.completed else "completed",
                    "priority": task.priority,
                    "category": task.category,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                    "is_recurring": task.is_recurring,
                    "recurrence_pattern": task.recurrence_pattern,
                    "next_recurrence": next_recurrence,
                })

            # Friendly message
            if len(tasks) == 0:
                message = "You don't have any tasks matching these filters."
            elif len(tasks) == 1:
                message = "Found 1 task"
            else:
                message = f"Found {len(tasks)} tasks"

            return {
                "success": True,
                "data": {
                    "tasks": task_list,
                    "count": len(tasks),
                    "filters": {
                        "status": input_data.status,
                        "priority": input_data.priority,
                        "category": input_data.category,
                        "search": input_data.search,
                    },
                    "sort": {
                        "by": input_data.sort_by,
                        "order": input_data.sort_order,
                    }
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
