"""
MCP (Model Context Protocol) Server for task management tools.

This package provides 5 stateless tools for todo operations:
- add_task: Create a new task
- list_tasks: Retrieve tasks with filtering
- complete_task: Mark a task as completed
- delete_task: Remove a task (soft delete)
- update_task: Modify task properties
"""

__all__ = ["MCPServer", "MCPToolRegistry"]
