"""
Response generation utilities for AI Agent.

Generates natural language responses for successful actions and errors.

Note: The OpenAI agent generates responses automatically, but these
templates ensure consistency and provide fallback formatting.
"""

from typing import List, Dict, Any
from datetime import datetime


def format_task_created_response(task_title: str, task_id: int, date_info: str = None) -> str:
    """
    Format response for successful task creation.

    Args:
        task_title: Task title
        task_id: Created task ID
        date_info: Optional date/time info

    Returns:
        Formatted response

    Example:
        "✓ Added 'buy milk' to your tasks (Task #1)"
    """
    response = f"✓ Added '{task_title}' to your tasks"

    if date_info:
        response += f" {date_info}"

    response += f" (Task #{task_id})"

    return response


def format_task_list_response(tasks: List[Dict[str, Any]]) -> str:
    """
    Format task list for display.

    Args:
        tasks: List of task dictionaries

    Returns:
        Formatted task list

    Example:
        "You have 3 tasks:
        1. Buy milk (pending)
        2. Call mom (pending)
        3. Finish report (pending)"
    """
    if not tasks:
        return "You don't have any tasks yet."

    count = len(tasks)
    plural = "task" if count == 1 else "tasks"
    response = f"You have {count} {plural}:\n"

    for i, task in enumerate(tasks, 1):
        status = "✓" if task.get("completed") else "○"
        title = task.get("title", "Untitled")
        task_id = task.get("task_id") or task.get("id")

        response += f"{i}. {status} {title}"

        if task_id:
            response += f" (#{task_id})"

        response += "\n"

    return response.rstrip()


def format_task_completed_response(task_title: str, task_id: int) -> str:
    """
    Format response for task completion.

    Args:
        task_title: Task title
        task_id: Task ID

    Returns:
        Formatted response
    """
    return f"✓ Marked '{task_title}' as completed! Great job! (Task #{task_id})"


def format_task_deleted_response(task_title: str, task_id: int) -> str:
    """
    Format response for task deletion.

    Args:
        task_title: Task title
        task_id: Task ID

    Returns:
        Formatted response
    """
    return f"✓ Deleted '{task_title}' from your tasks (Task #{task_id})"


def format_task_updated_response(task_title: str, task_id: int, changes: str) -> str:
    """
    Format response for task update.

    Args:
        task_title: Task title
        task_id: Task ID
        changes: Description of changes

    Returns:
        Formatted response
    """
    return f"✓ Updated '{task_title}' - {changes} (Task #{task_id})"


def format_error_response(error_type: str, detail: str = None) -> str:
    """
    Format user-friendly error response.

    Args:
        error_type: Type of error
        detail: Optional error detail

    Returns:
        User-friendly error message
    """
    error_messages = {
        "VALIDATION_ERROR": "I couldn't process that request. Please check your input and try again.",
        "NOT_FOUND": "I couldn't find that task. Please make sure it exists.",
        "FORBIDDEN": "You don't have permission to access that task.",
        "SERVER_ERROR": "Something went wrong on my end. Please try again in a moment.",
    }

    message = error_messages.get(error_type, "An error occurred. Please try again.")

    if detail:
        message += f" ({detail})"

    return message
