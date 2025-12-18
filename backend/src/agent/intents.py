"""
Intent detection for AI Agent.

Defines intent categories and trigger phrases for natural language understanding.

Intents:
- Add: Creating new tasks
- List: Viewing tasks
- Complete: Marking tasks as done
- Delete: Removing tasks
- Update: Modifying tasks
"""

from typing import Optional, List
from enum import Enum
import re


class Intent(str, Enum):
    """Intent enumeration for task management."""

    ADD = "add"
    LIST = "list"
    COMPLETE = "complete"
    DELETE = "delete"
    UPDATE = "update"
    UNKNOWN = "unknown"


# Intent trigger phrases
# Note: The OpenAI agent handles intent detection via the system prompt,
# but these definitions serve as documentation and can be used for
# rule-based fallback if needed

ADD_INTENT_TRIGGERS = [
    r"\b(add|create|new|make)\s+(a\s+)?(task|todo|item)",
    r"\b(remind|remember)\s+me\s+to\b",
    r"\b(i\s+need|i\s+have)\s+to\b",
    r"\b(i\s+should|i\s+want\s+to)\b",
    r"\b(put|add)\s+.+\s+(on|to)\s+(my\s+)?(list|tasks)",
]

LIST_INTENT_TRIGGERS = [
    r"\b(show|list|display|view|see)\s+(my\s+)?(tasks|todos|items)",
    r"\bwhat(\s+are|\s+is|\')s?\s+(my\s+)?(tasks|todos)",
    r"\bwhat(\s+do\s+i\s+have|\'s\s+on\s+my\s+list)",
    r"\b(what|show)\s+(is\s+)?due\b",
    r"\bany\s+tasks\b",
]

COMPLETE_INTENT_TRIGGERS = [
    r"\b(mark|set)\s+.+\s+(as\s+)?(done|complete|completed|finished)",
    r"\b(complete|finish|done\s+with)\s+.+",
    r"\b(i\s+)?(completed|finished|did)\s+.+",
    r"\bcheck\s+off\b",
]

DELETE_INTENT_TRIGGERS = [
    r"\b(delete|remove|get\s+rid\s+of)\s+.+",
    r"\b(cancel|drop)\s+.+\s+task",
    r"\bdon\'t\s+need\s+.+\s+anymore",
]

UPDATE_INTENT_TRIGGERS = [
    r"\b(change|update|modify|edit)\s+.+",
    r"\brename\s+.+\s+to\b",
    r"\bmake\s+.+\s+(say|be)\b",
]


def detect_intent_rule_based(message: str) -> Intent:
    """
    Detect intent using rule-based pattern matching (fallback method).

    This function is provided as a fallback if OpenAI's function calling
    doesn't properly identify the intent. In practice, the OpenAI agent
    handles intent detection via the system prompt.

    Args:
        message: User's message

    Returns:
        Detected intent (or UNKNOWN if no match)
    """
    message_lower = message.lower()

    # Check Add intent
    for pattern in ADD_INTENT_TRIGGERS:
        if re.search(pattern, message_lower):
            return Intent.ADD

    # Check List intent
    for pattern in LIST_INTENT_TRIGGERS:
        if re.search(pattern, message_lower):
            return Intent.LIST

    # Check Complete intent
    for pattern in COMPLETE_INTENT_TRIGGERS:
        if re.search(pattern, message_lower):
            return Intent.COMPLETE

    # Check Delete intent
    for pattern in DELETE_INTENT_TRIGGERS:
        if re.search(pattern, message_lower):
            return Intent.DELETE

    # Check Update intent
    for pattern in UPDATE_INTENT_TRIGGERS:
        if re.search(pattern, message_lower):
            return Intent.UPDATE

    return Intent.UNKNOWN


def get_intent_description(intent: Intent) -> str:
    """
    Get human-readable description of an intent.

    Args:
        intent: Intent enum value

    Returns:
        Description string
    """
    descriptions = {
        Intent.ADD: "Creating a new task",
        Intent.LIST: "Viewing tasks",
        Intent.COMPLETE: "Marking a task as completed",
        Intent.DELETE: "Deleting a task",
        Intent.UPDATE: "Updating a task",
        Intent.UNKNOWN: "Unknown action",
    }
    return descriptions.get(intent, "Unknown")
