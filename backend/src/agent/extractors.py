"""
Parameter extraction utilities for AI Agent.

Extracts structured parameters from natural language:
- Task titles
- Status filters (pending/completed/all)
- Task references (by title or ID)
- Dates and times
"""

from typing import Optional, List, Dict, Any
import re


def extract_task_title(message: str) -> Optional[str]:
    """
    Extract task title from natural language message.

    This is a rule-based fallback. In practice, the OpenAI agent
    extracts parameters via function calling.

    Args:
        message: User's message

    Returns:
        Extracted task title or None

    Examples:
        "Add buy milk" -> "buy milk"
        "Remind me to call mom tomorrow" -> "call mom tomorrow"
        "I need to finish the report" -> "finish the report"
    """
    message_lower = message.lower().strip()

    # Pattern: "add/create/make <title>"
    match = re.search(
        r"(?:add|create|make|new)\s+(?:a\s+)?(?:task\s+)?(?:to\s+)?(.+)",
        message_lower,
    )
    if match:
        return match.group(1).strip()

    # Pattern: "remind me to <title>"
    match = re.search(r"remind\s+me\s+to\s+(.+)", message_lower)
    if match:
        return match.group(1).strip()

    # Pattern: "I need/want/have to <title>"
    match = re.search(r"i\s+(?:need|want|have)\s+to\s+(.+)", message_lower)
    if match:
        return match.group(1).strip()

    # Pattern: "I should <title>"
    match = re.search(r"i\s+should\s+(.+)", message_lower)
    if match:
        return match.group(1).strip()

    return None


def extract_status_filter(message: str) -> str:
    """
    Extract status filter from message.

    Args:
        message: User's message

    Returns:
        Status filter: "all", "pending", or "completed"

    Examples:
        "show my pending tasks" -> "pending"
        "what's completed" -> "completed"
        "list all tasks" -> "all"
    """
    message_lower = message.lower()

    if re.search(r"\b(pending|active|open|incomplete)\b", message_lower):
        return "pending"

    if re.search(r"\b(completed|done|finished)\b", message_lower):
        return "completed"

    # Default to all
    return "all"


def extract_task_reference(message: str, available_tasks: List[Dict[str, Any]]) -> Optional[int]:
    """
    Extract task reference (by ID or title) from message.

    Args:
        message: User's message
        available_tasks: List of available tasks with id and title

    Returns:
        Task ID if found, None otherwise

    Examples:
        "complete task 5" -> 5
        "delete buy milk" -> (looks up task with title "buy milk")
        "mark that task done" -> (requires conversation context)
    """
    message_lower = message.lower().strip()

    # Pattern: "task <id>" or "#<id>"
    match = re.search(r"(?:task\s+)?#?(\d+)", message_lower)
    if match:
        task_id = int(match.group(1))
        # Verify task exists
        if any(task["id"] == task_id for task in available_tasks):
            return task_id

    # Pattern: match task title
    for task in available_tasks:
        task_title_lower = task["title"].lower()
        if task_title_lower in message_lower:
            return task["id"]

    return None


def clean_title(title: str) -> str:
    """
    Clean and normalize task title.

    Args:
        title: Raw title text

    Returns:
        Cleaned title

    Examples:
        "  buy milk  " -> "buy milk"
        "BUY MILK" -> "Buy milk"
    """
    # Strip whitespace
    title = title.strip()

    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]

    return title
