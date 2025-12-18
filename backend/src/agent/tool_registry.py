"""
MCP Tool Registry for OpenAI Agent Function Calling.

This module integrates the MCP tools with OpenAI's function calling
mechanism, allowing the agent to invoke task management tools.
"""

from typing import List, Dict, Any
import logging
from ..mcp_server.server import tool_registry

logger = logging.getLogger(__name__)


def get_openai_tools() -> List[Dict[str, Any]]:
    """
    Get all MCP tools formatted for OpenAI function calling.

    Returns:
        List of tool schemas compatible with OpenAI function calling API

    Example:
        tools = get_openai_tools()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
    """
    try:
        schemas = tool_registry.get_all_schemas()
        logger.info(f"Retrieved {len(schemas)} tool schemas for OpenAI agent")
        return schemas
    except Exception as e:
        logger.error(f"Error getting OpenAI tools: {e}")
        # Return empty list if tools not yet registered
        # This allows the module to import without errors during setup
        return []


def get_tool_names() -> List[str]:
    """
    Get list of all registered MCP tool names.

    Returns:
        List of tool names (e.g., ["add_task", "list_tasks", ...])
    """
    try:
        return tool_registry.list_tools()
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return []


async def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP tool call from the OpenAI agent.

    Args:
        tool_name: Name of the tool to execute (e.g., "add_task")
        arguments: Tool arguments as dictionary

    Returns:
        Tool execution result

    Raises:
        KeyError: If tool not found
        Exception: If tool execution fails
    """
    try:
        tool = tool_registry.get_tool(tool_name)
        logger.info(f"Executing MCP tool: {tool_name} with args: {arguments}")

        # Execute the tool (tools are async functions)
        result = await tool(**arguments)

        logger.info(f"Tool {tool_name} executed successfully")
        logger.debug(f"Tool result type: {type(result)}, content: {result}")
        return result

    except KeyError:
        logger.error(f"Tool not found: {tool_name}")
        raise
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        raise
