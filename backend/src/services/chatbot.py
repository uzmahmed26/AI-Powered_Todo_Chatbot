"""
AI Chatbot Service using OpenAI Agents SDK
============================================================================
Phase III: Intelligent chatbot for managing todos with natural language
This service integrates OpenAI's API to provide conversational AI capabilities
"""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import json
import os


class TodoChatbot:
    """
    AI-powered chatbot for todo management

    Features:
    - Add tasks via natural language
    - Query tasks intelligently
    - Update and delete tasks conversationally
    - Maintain context across conversations
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the chatbot with OpenAI client"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for cost efficiency

        # System prompt that defines the chatbot's behavior
        self.system_prompt = """You are a helpful AI assistant for managing todo tasks.
You help users add, view, update, and delete their tasks through natural conversation.

When users want to:
- ADD a task: Extract the task title, description (if any), and priority
- VIEW tasks: Show tasks in a clear, organized format
- UPDATE a task: Identify which task and what to update
- DELETE a task: Confirm which task to remove
- QUERY tasks: Search or filter based on user criteria

Always be concise, friendly, and helpful. Format responses clearly."""

    async def chat(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        available_tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response

        Args:
            user_message: The user's input message
            conversation_history: Previous messages in the conversation
            available_tools: Function tools available for the AI to call

        Returns:
            Dict containing response and any tool calls
        """

        # Build messages list
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }

        # Add tools if available
        if available_tools:
            api_params["tools"] = available_tools
            api_params["tool_choice"] = "auto"

        # Call OpenAI API
        response = await self.client.chat.completions.create(**api_params)

        # Extract response
        message = response.choices[0].message

        result = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": []
        }

        # Check for tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    }
                }
                for tool_call in message.tool_calls
            ]

        return result

    def get_todo_tools(self) -> List[Dict[str, Any]]:
        """
        Define function tools for todo operations
        These tools allow the AI to call backend functions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Add a new task to the todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The task title or description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Task priority level"
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format (optional)"
                            }
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_tasks",
                    "description": "Get all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter tasks by status"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Filter by priority (optional)"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)"
                            },
                            "completed": {
                                "type": "boolean",
                                "description": "Mark as completed/incomplete (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "New priority level (optional)"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task from the todo list",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                }
            }
        ]


# Example usage function
async def example_chatbot_interaction():
    """Example of how to use the chatbot"""

    chatbot = TodoChatbot()
    tools = chatbot.get_todo_tools()

    # Conversation history
    conversation = []

    # User asks to add a task
    user_msg = "Add a task to buy groceries tomorrow with high priority"

    response = await chatbot.chat(
        user_message=user_msg,
        conversation_history=conversation,
        available_tools=tools
    )

    print(f"User: {user_msg}")
    print(f"Assistant: {response['content']}")

    # Check if AI wants to call a tool
    if response['tool_calls']:
        for tool_call in response['tool_calls']:
            print(f"Tool Call: {tool_call['function']['name']}")
            print(f"Arguments: {tool_call['function']['arguments']}")

    return response
