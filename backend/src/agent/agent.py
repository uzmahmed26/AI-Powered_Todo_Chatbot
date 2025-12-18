"""
TodoAgent: AI Agent for natural language task management.

This module provides the main agent class that orchestrates:
- Intent recognition (Add, List, Complete, Delete, Update)
- Parameter extraction from natural language
- MCP tool invocation
- Natural language response generation
"""

from typing import List, Dict, Any, Optional
import logging
import json
from openai import AsyncOpenAI
from .client import get_async_openai_client, get_model_config, MAX_CONTEXT_MESSAGES
from .tool_registry import get_openai_tools, execute_tool_call

logger = logging.getLogger(__name__)


class TodoAgent:
    """
    AI Agent for natural language todo management.

    The agent uses OpenAI's GPT-4 with function calling to:
    1. Understand user intent from natural language
    2. Extract task parameters (title, status, task ID, etc.)
    3. Invoke appropriate MCP tools
    4. Generate natural language responses

    Example:
        agent = TodoAgent(user_id="auth0|abc123")
        response = await agent.process_message(
            message="Add buy milk to my tasks",
            conversation_history=[]
        )
    """

    def __init__(self, user_id: str):
        """
        Initialize the TodoAgent.

        Args:
            user_id: User ID from Better Auth (for tool invocations)
        """
        self.user_id = user_id
        self.client: Optional[AsyncOpenAI] = None
        self.model_config = get_model_config()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the agent.

        Returns:
            System prompt defining agent behavior
        """
        return """You are a helpful AI assistant for managing todo tasks. Your actions are performed for a specific user, and you already know their user_id. You must not ask for it.

Your role is to:

1. **Understand user intent** from natural language:
   - "Add" intent: Creating new tasks (trigger phrases: "add", "create", "remind me", "I need to")
   - "List" intent: Viewing tasks (trigger phrases: "show", "list", "what are my tasks", "what's due")
   - "Complete" intent: Marking tasks done (trigger phrases: "mark done", "complete", "finish")
   - "Delete" intent: Removing tasks (trigger phrases: "delete", "remove", "get rid of")
   - "Update" intent: Modifying tasks (trigger phrases: "change", "update", "modify")

2. **Extract parameters** from natural language:
   - Task titles (e.g., "buy milk" from "remind me to buy milk")
   - Status filters (e.g., "pending", "completed", "all")
   - Task references (e.g., "buy groceries", "that task", "the report")
   - Dates/times (e.g., "tomorrow", "next Friday") - store in description for now

3. **Use available tools**:
   - add_task: Create new tasks
   - list_tasks: View tasks with optional status filter
   - complete_task: Mark tasks as completed
   - delete_task: Remove tasks
   - update_task: Modify task properties

4. **Respond naturally**:
   - Confirm successful actions ("✓ Added 'buy milk' to your tasks")
   - Format task lists clearly
   - Ask for clarification if information is missing
   - Translate technical errors to user-friendly messages
   - Never expose technical details or stack traces

5. **Rules**:
   - You are operating on behalf of a user with a pre-configured user_id. You must never ask for a user_id.
   - Always confirm successful actions
   - Ask clarification if task title or ID is missing
   - Never fabricate task data
   - Chain tools if needed (e.g., list then complete)
   - Use conversation context to resolve references

Be helpful, concise, and user-friendly!"""

    async def _initialize_client(self) -> None:
        """Initialize OpenAI client if not already initialized."""
        if self.client is None:
            self.client = get_async_openai_client()

    def _build_messages(
        self, message: str, conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Build message list for OpenAI API.

        Args:
            message: New user message
            conversation_history: Previous messages (list of {"role": "user/assistant", "content": "..."})

        Returns:
            Complete message list with system prompt
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history (last N messages for context)
        if conversation_history:
            recent_history = conversation_history[-MAX_CONTEXT_MESSAGES:]
            messages.extend(recent_history)

        # Add new user message
        messages.append({"role": "user", "content": message})

        return messages

    async def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        This method:
        1. Initializes OpenAI client
        2. Builds message context
        3. Calls OpenAI API with function calling
        4. Executes any tool calls
        5. Generates final response

        Args:
            message: User's message
            conversation_history: Previous conversation messages

        Returns:
            Dictionary with:
                - response: Agent's text response
                - tool_calls: List of tools invoked (for logging)
                - success: Whether processing succeeded

        Example:
            result = await agent.process_message(
                message="Add buy milk to my tasks",
                conversation_history=[]
            )
            # Result: {
            #   "response": "✓ Added 'buy milk' to your tasks",
            #   "tool_calls": [{"tool": "add_task", "args": {...}}],
            #   "success": True
            # }
        """
        try:
            await self._initialize_client()

            if conversation_history is None:
                conversation_history = []

            # Build messages for OpenAI
            messages = self._build_messages(message, conversation_history)

            # Get available tools
            tools = get_openai_tools()

            # Call OpenAI API with function calling
            logger.info(f"Calling OpenAI API for user: {self.user_id}")
            response = await self.client.chat.completions.create(
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                **self.model_config,
            )

            tool_calls_made = []
            assistant_message = response.choices[0].message

            # Check if agent wants to call tools
            if assistant_message.tool_calls:
                logger.info(f"Agent requested {len(assistant_message.tool_calls)} tool calls")

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # Inject user_id into tool arguments
                    tool_args["user_id"] = self.user_id

                    logger.info(f"Executing tool: {tool_name}")
                    logger.info(f"Tool input: {json.dumps(tool_args, indent=2)}")

                    # Execute the tool
                    tool_result = await execute_tool_call(tool_name, tool_args)

                    logger.info(f"Tool output: {json.dumps(tool_result, indent=2)}")

                    tool_calls_made.append(
                        {
                            "tool": tool_name,
                            "args": tool_args,
                            "result": tool_result,
                        }
                    )

                # Build follow-up message with tool results
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ],
                    }
                )

                # Add tool results
                for i, tool_call in enumerate(assistant_message.tool_calls):
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": json.dumps(tool_calls_made[i]["result"]),
                        }
                    )

                # Get final response from agent
                final_response = await self.client.chat.completions.create(
                    messages=messages,
                    **self.model_config,
                )

                final_text = final_response.choices[0].message.content

            else:
                # No tool calls needed, use direct response
                final_text = assistant_message.content

            logger.info("Agent processing completed successfully")

            return {
                "response": final_text,
                "tool_calls": tool_calls_made,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "success": False,
                "error": str(e),
            }
