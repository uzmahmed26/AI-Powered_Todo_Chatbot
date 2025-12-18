"""
Clarification prompt generation for AI Agent.

Generates user-friendly clarification questions when information is missing.

Note: The OpenAI agent handles clarification prompts automatically via
its system prompt, but these helpers provide templates for consistency.
"""

from typing import Optional


def get_missing_title_clarification() -> str:
    """
    Get clarification prompt when task title is missing.

    Returns:
        Clarification question
    """
    return (
        "I'd be happy to help you create a task! "
        "Could you please tell me what you'd like to be reminded about?"
    )


def get_missing_task_reference_clarification() -> str:
    """
    Get clarification prompt when task reference is ambiguous.

    Returns:
        Clarification question
    """
    return (
        "I'm not sure which task you're referring to. "
        "Could you provide more details or the task number?"
    )


def get_confirm_action_prompt(action: str, task_title: str) -> str:
    """
    Get confirmation prompt for an action.

    Args:
        action: Action type (e.g., "delete", "complete")
        task_title: Task title

    Returns:
        Confirmation question
    """
    return f"Are you sure you want to {action} '{task_title}'?"


def get_empty_list_response(filter_status: str = "all") -> str:
    """
    Get response for empty task list.

    Args:
        filter_status: Filter applied ("all", "pending", "completed")

    Returns:
        User-friendly message
    """
    if filter_status == "pending":
        return "You don't have any pending tasks. Great job staying on top of things! 🎉"
    elif filter_status == "completed":
        return "You haven't completed any tasks yet. Keep working on it!"
    else:
        return "You don't have any tasks yet. Let me know when you'd like to add one!"
