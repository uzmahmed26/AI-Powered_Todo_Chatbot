"""
MCP Server for Phase III Smart Todo ChatKit App.

This module provides the MCP server implementation with tool registration
for the 5 task management tools. The server is stateless and designed to
be called by the OpenAI Agent via function calling.

Note: This implementation uses a function-based approach compatible with
OpenAI function calling. When the official MCP SDK is available, this
can be adapted to use the SDK's server implementation.
"""

from typing import Dict, Any, Callable, List
import logging
from .schemas import (
    AddTaskInput,
    AddTaskOutput,
    ListTasksInput,
    ListTasksOutput,
    CompleteTaskInput,
    CompleteTaskOutput,
    DeleteTaskInput,
    DeleteTaskOutput,
    UpdateTaskInput,
    UpdateTaskOutput,
    MCPErrorResponse,
)

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """
    Registry for MCP tools.

    Maintains a mapping of tool names to their implementations
    and schemas for OpenAI function calling.
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register_tool(
        self,
        name: str,
        handler: Callable,
        schema: Dict[str, Any],
    ) -> None:
        """
        Register a tool with the MCP server.

        Args:
            name: Tool name (e.g., "add_task")
            handler: Tool implementation function
            schema: OpenAI function calling schema
        """
        self._tools[name] = handler
        self._schemas[name] = schema
        logger.info(f"Registered MCP tool: {name}")

    def get_tool(self, name: str) -> Callable:
        """
        Get a tool implementation by name.

        Args:
            name: Tool name

        Returns:
            Tool handler function

        Raises:
            KeyError: If tool not found
        """
        if name not in self._tools:
            raise KeyError(f"MCP tool '{name}' not found")
        return self._tools[name]

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Get all tool schemas for OpenAI function calling.

        Returns:
            List of OpenAI function schemas
        """
        return list(self._schemas.values())

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())


# Global tool registry instance
tool_registry = MCPToolRegistry()


def register_all_tools() -> MCPToolRegistry:
    """
    Register all MCP tools with the registry.

    This function registers the 5 task management tools:
    - add_task
    - list_tasks
    - complete_task
    - delete_task
    - update_task

    Returns:
        Configured MCPToolRegistry instance
    """
    from .tools import add_task, list_tasks
    # TODO: Import other tools when implemented in User Story 2
    # from .tools import complete_task, delete_task, update_task

    # Register add_task
    tool_registry.register_tool(
        name="add_task",
        handler=add_task.execute,
        schema={
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Better Auth",
                        },
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description",
                        },
                    },
                    "required": ["user_id", "title"],
                },
            },
        },
    )

    # Register list_tasks
    tool_registry.register_tool(
        name="list_tasks",
        handler=list_tasks.execute,
        schema={
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks for the user with optional status filter",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID from Better Auth",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter by status",
                            "default": "all",
                        },
                    },
                    "required": ["user_id"],
                },
            },
        },
    )

    # TODO: Register complete_task when implemented in User Story 2
    # tool_registry.register_tool(
    #     name="complete_task",
    #     handler=complete_task.execute,
    #     schema={
    #         "type": "function",
    #         "function": {
    #             "name": "complete_task",
    #             "description": "Mark a task as completed",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "user_id": {
    #                         "type": "string",
    #                         "description": "User ID from Better Auth",
    #                     },
    #                     "task_id": {
    #                         "type": "integer",
    #                         "description": "ID of the task to complete",
    #                     },
    #                 },
    #                 "required": ["user_id", "task_id"],
    #             },
    #         },
    #     },
    # )

    # TODO: Register delete_task when implemented in User Story 2
    # tool_registry.register_tool(
    #     name="delete_task",
    #     handler=delete_task.execute,
    #     schema={
    #         "type": "function",
    #         "function": {
    #             "name": "delete_task",
    #             "description": "Delete a task (soft delete)",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "user_id": {
    #                         "type": "string",
    #                         "description": "User ID from Better Auth",
    #                     },
    #                     "task_id": {
    #                         "type": "integer",
    #                         "description": "ID of the task to delete",
    #                     },
    #                 },
    #                 "required": ["user_id", "task_id"],
    #             },
    #         },
    #     },
    # )

    # TODO: Register update_task when implemented in User Story 2
    # tool_registry.register_tool(
    #     name="update_task",
    #     handler=update_task.execute,
    #     schema={
    #         "type": "function",
    #         "function": {
    #             "name": "update_task",
    #             "description": "Update task properties (title and/or description)",
    #             "parameters": {
    #                 "type": "object",
    #                 "properties": {
    #                     "user_id": {
    #                         "type": "string",
    #                         "description": "User ID from Better Auth",
    #                     },
    #                     "task_id": {
    #                         "type": "integer",
    #                         "description": "ID of the task to update",
    #                     },
    #                     "title": {
    #                         "type": "string",
    #                         "description": "New task title (optional)",
    #                     },
    #                     "description": {
    #                         "type": "string",
    #                         "description": "New task description (optional)",
    #                     },
    #                 },
    #                 "required": ["user_id", "task_id"],
    #             },
    #         },
    #     },
    # )

    logger.info(f"Registered {len(tool_registry.list_tools())} MCP tools")
    return tool_registry


# Initialize tools on module import
# Note: Tool implementations will be created in Phase 3
# For now, this will fail gracefully if tools package doesn't exist
try:
    register_all_tools()
except ImportError:
    logger.warning("MCP tool implementations not yet available - will register when tools are created")
