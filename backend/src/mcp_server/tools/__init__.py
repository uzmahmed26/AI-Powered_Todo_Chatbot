"""
MCP Tool implementations for task management.

This package contains the 5 stateless MCP tools:
- add_task: Create new tasks
- list_tasks: Retrieve tasks with filtering
- complete_task: Mark tasks as completed
- delete_task: Remove tasks (soft delete)
- update_task: Modify task properties
"""

# Import tool implementations as they are created
from . import add_task, list_tasks, complete_task, delete_task, update_task

__all__ = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
