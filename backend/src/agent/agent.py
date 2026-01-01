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
from ..i18n.detector import LanguageDetector
from ..i18n.translator import TranslationService

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

    def __init__(self, user_id: str, language: str = "en"):
        """
        Initialize the TodoAgent.

        Args:
            user_id: User ID from Better Auth (for tool invocations)
            language: Language code for responses (en or ur, default: en)
        """
        self.user_id = user_id
        self.language = language
        self.client: Optional[AsyncOpenAI] = None
        self.model_config = get_model_config()
        self.system_prompt = self._build_system_prompt(language)
        self.translator: Optional[TranslationService] = None

    def _build_system_prompt(self, language: str = "en") -> str:
        """
        Build the system prompt for the agent.

        Args:
            language: Language code for responses (en or ur)

        Returns:
            System prompt defining agent behavior
        """
        language_instruction = ""
        if language == "ur":
            language_instruction = "\n\n**IMPORTANT: You must respond in Urdu language. All your responses, confirmations, and messages must be in Urdu (اردو).**\n"

        return f"""You are a helpful AI assistant for managing todo tasks. Your actions are performed for a specific user, and you already know their user_id. You must not ask for it.{language_instruction}

Your role is to:

1. **Understand user intent** from natural language:
   - "Add" intent: Creating new tasks (trigger phrases: "add", "create", "remind me", "I need to")
   - "List" intent: Viewing tasks (trigger phrases: "show", "list", "what are my tasks", "what's due")
   - "Complete" intent: Marking tasks done (trigger phrases: "mark done", "complete", "finish")
   - "Delete" intent: Removing tasks (trigger phrases: "delete", "remove", "get rid of")
   - "Update" intent: Modifying tasks (trigger phrases: "change", "update", "modify")

2. **Extract parameters** from natural language:
   - Task titles (e.g., "buy milk" from "remind me to buy milk")
   - Priority levels (extract from: "urgent", "important", "critical", "high priority" → high; "normal", "regular" → medium; "later", "whenever", "low priority" → low)
   - Categories (extract from: "work", "job", "office" → work; "home", "house" → home; "study", "school" → study; "shopping", "groceries", "buy" → shopping; "health", "doctor" → health; "fitness", "gym" → fitness)
   - Due dates (parse: "today", "tonight", "tomorrow", "next week", "next Monday", "January 15", "in 3 days" → convert to ISO datetime)
   - Status filters (e.g., "pending", "completed", "all")
   - Task references (e.g., "buy groceries", "that task", "the report")

3. **Use available tools**:
   - add_task: Create new tasks (supports: title, description, priority, category, due_date, recurrence settings)
   - list_tasks: View tasks with advanced filtering (supports: status, priority, category, search, due_date_from, due_date_to, sort_by, sort_order)
   - complete_task: Mark tasks as completed (auto-creates next instance for recurring tasks)
   - delete_task: Remove tasks
   - update_task: Modify task properties (supports: title, description, priority, category, due_date)

4. **Task fields available**:
   - title (required): Task name
   - description (optional): Task details
   - priority (optional): "high", "medium" (default), "low"
   - category (optional): "work", "home", "study", "personal", "shopping", "health", "fitness"
   - due_date (optional): ISO datetime string (e.g., "2025-01-15T10:00:00Z")
   - is_recurring (optional): true/false - whether task repeats
   - recurrence_pattern (optional): "daily", "weekly", "monthly"
   - recurrence_interval (optional): number (default: 1) - how often to recur (e.g., every 2 days)
   - recurrence_end_date (optional): ISO datetime - when recurrence should stop

5. **Natural language extraction examples**:
   Priority:
   - "Add urgent task to fix bug" → priority="high"
   - "Add important work task" → priority="high"
   - "Add normal task to buy milk" → priority="medium"
   - "Add low priority task for later" → priority="low"

   Category:
   - "Add work task to finish report" → category="work"
   - "Add home task to fix sink" → category="home"
   - "Add shopping task for groceries" → category="shopping"
   - "Buy eggs" → category="shopping" (infer from "buy")

   Due dates:
   - "due today" → today at 23:59
   - "due tomorrow" → tomorrow at 12:00
   - "due next week" → 7 days from now
   - "due January 15" → 2025-01-15T12:00:00Z
   - "due in 3 days" → 3 days from now at 12:00

   Recurrence patterns:
   - "every day" → is_recurring=true, recurrence_pattern="daily"
   - "daily" → is_recurring=true, recurrence_pattern="daily"
   - "every 2 days" → is_recurring=true, recurrence_pattern="daily", recurrence_interval=2
   - "every week" → is_recurring=true, recurrence_pattern="weekly"
   - "weekly" → is_recurring=true, recurrence_pattern="weekly"
   - "every Monday" → is_recurring=true, recurrence_pattern="weekly"
   - "every month" → is_recurring=true, recurrence_pattern="monthly"
   - "monthly" → is_recurring=true, recurrence_pattern="monthly"
   - "every day until January 31" → is_recurring=true, recurrence_pattern="daily", recurrence_end_date="2025-01-31T23:59:59Z"

6. **Filtering and sorting**:
   When user asks to filter or search:
   - "show high priority tasks" → list_tasks(priority="high")
   - "list my work tasks" → list_tasks(category="work")
   - "find tasks with report" → list_tasks(search="report")
   - "tasks due this week" → list_tasks(due_date_from="<today>", due_date_to="<end of week>")
   - "sort by due date" → list_tasks(sort_by="due_date", sort_order="asc")
   - "sort by priority" → list_tasks(sort_by="priority", sort_order="desc")

7. **Respond naturally**:
   - Confirm successful actions with details ("✓ Added 'fix bug' (Task #5) - Priority: high, Category: work, Due: Jan 15")
   - Format task lists clearly showing priority, category, and due date
   - Ask for clarification if information is missing
   - Translate technical errors to user-friendly messages
   - Never expose technical details or stack traces

8. **Rules**:
   - You are operating on behalf of a user with a pre-configured user_id. You must never ask for a user_id.
   - Always extract priority, category, and due date from natural language when mentioned
   - Always confirm successful actions with relevant details
   - Ask clarification if task title or ID is missing
   - Never fabricate task data
   - Chain tools if needed (e.g., list then complete)
   - Use conversation context to resolve references

Be helpful, concise, and user-friendly!"""

    async def _initialize_client(self) -> None:
        """Initialize OpenAI client and translator if not already initialized."""
        if self.client is None:
            self.client = get_async_openai_client()
        if self.translator is None:
            self.translator = TranslationService(self.client)

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

            # MULTI-LANGUAGE SUPPORT: Detect language and translate to English
            detected_lang = LanguageDetector.detect(message)
            logger.info(f"Detected language: {LanguageDetector.get_language_name(detected_lang)}")

            # Translate user message to English if needed
            english_message = message
            if detected_lang != "en":
                english_message = await self.translator.translate_to_english(message, detected_lang)
                logger.info(f"Translated to English: {english_message}")

            # Build messages for OpenAI (using English message)
            messages = self._build_messages(english_message, conversation_history)

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

            # MULTI-LANGUAGE SUPPORT: Translate response back to user's language
            if detected_lang != "en" and final_text:
                final_text = await self.translator.translate_from_english(final_text, detected_lang)
                logger.info(f"Translated response to {LanguageDetector.get_language_name(detected_lang)}")

            logger.info("Agent processing completed successfully")

            return {
                "response": final_text,
                "tool_calls": tool_calls_made,
                "success": True,
                "detected_language": detected_lang,
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": "I'm sorry, I encountered an error processing your request. Please try again.",
                "tool_calls": [],
                "success": False,
                "error": str(e),
            }
