# Phase III: AI-Powered Todo Chatbot Integration Guide

## Overview

Phase III integrates OpenAI's GPT models to create an intelligent chatbot that can manage todos through natural language conversation.

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────▶│   Backend    │─────▶│   OpenAI     │
│  (React/TS)  │      │   (FastAPI)  │      │     API      │
└──────────────┘      └──────────────┘      └──────────────┘
       │                      │
       │                      │
       └──────────────────────┘
          Conversation State
```

## Features

### 1. Natural Language Task Management
- **Add Tasks**: "Add a task to buy groceries tomorrow"
- **View Tasks**: "Show me all my high priority tasks"
- **Update Tasks**: "Mark task #5 as completed"
- **Delete Tasks**: "Remove the grocery shopping task"

### 2. Function Calling
The chatbot uses OpenAI's function calling feature to execute actions:
- `add_task(title, priority, due_date)`
- `get_tasks(status, priority)`
- `update_task(task_id, ...)`
- `delete_task(task_id)`

### 3. Context Management
Maintains conversation history for natural, contextual interactions.

## Backend Implementation

### Chatbot Service (`backend/src/services/chatbot.py`)

```python
from openai import AsyncOpenAI

class TodoChatbot:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4"

    async def chat(self, user_message, history, tools):
        # Process message with OpenAI
        # Return response and tool calls
```

### API Routes (`backend/src/api/chatbot_routes.py`)

```python
@router.post("/api/chatbot/chat")
async def chat_endpoint(request: ChatRequest):
    # Handle chat requests
    # Execute tool calls if needed
    # Return AI response
```

## Frontend Implementation

### Chatbot Service (`frontend/src/services/chatbotService.ts`)

```typescript
export class ChatbotService {
  async sendMessage(message: string): Promise<ChatResponse> {
    // Send to backend
    // Process tool calls
    // Return response
  }
}
```

### React Component (Example)

```tsx
import { chatbotService } from './services/chatbotService';

function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const sendMessage = async (text: string) => {
    const response = await chatbotService.sendMessage(text);

    // Process tool calls if any
    if (response.tool_calls) {
      await chatbotService.processToolCalls(response.tool_calls);
    }

    // Update UI with response
    setMessages([...messages, { role: 'assistant', content: response.message }]);
  };

  return (
    // Chat UI components
  );
}
```

## Configuration

### Environment Variables

```bash
# Backend (.env)
OPENAI_API_KEY=YOUR_API_KEY_HERE
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo

# Frontend (.env)
VITE_API_URL=http://localhost:8000/api
```

### Requirements

Add to `backend/requirements.txt`:
```
openai>=1.0.0
```

Add to `frontend/package.json`:
```json
{
  "dependencies": {
    "axios": "^1.6.0"
  }
}
```

## Usage Examples

### 1. Adding a Task

**User**: "I need to finish the report by Friday with high priority"

**AI Response**: "I've added the task 'Finish the report' with high priority and due date 2024-12-29. Anything else?"

**Tool Call**:
```json
{
  "function": "add_task",
  "arguments": {
    "title": "Finish the report",
    "priority": "high",
    "due_date": "2024-12-29"
  }
}
```

### 2. Viewing Tasks

**User**: "What are my pending high priority tasks?"

**AI Response**: "You have 2 high priority pending tasks:
1. Finish the report (Due: 2024-12-29)
2. Team meeting preparation (Due: 2024-12-28)"

**Tool Call**:
```json
{
  "function": "get_tasks",
  "arguments": {
    "status": "pending",
    "priority": "high"
  }
}
```

### 3. Updating Tasks

**User**: "Mark task 5 as done"

**AI Response**: "Great! I've marked task #5 as completed."

**Tool Call**:
```json
{
  "function": "update_task",
  "arguments": {
    "task_id": 5,
    "completed": true
  }
}
```

## Testing

### Test the Chatbot Service

```python
# backend/tests/test_chatbot.py
import pytest
from src.services.chatbot import TodoChatbot

@pytest.mark.asyncio
async def test_chatbot_response():
    chatbot = TodoChatbot(api_key="test-key")
    response = await chatbot.chat("Add a task to test")
    assert response["content"] is not None
```

### Test API Endpoints

```bash
curl -X POST http://localhost:8000/api/chatbot/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all tasks",
    "conversation_history": [],
    "use_tools": true
  }'
```

## Deployment Considerations

### 1. API Key Security
- **Never commit API keys to git**
- Use Kubernetes secrets for production
- Rotate keys regularly

### 2. Rate Limiting
- Implement rate limiting to control costs
- Monitor OpenAI API usage

### 3. Error Handling
- Handle API failures gracefully
- Provide fallback responses
- Log errors for debugging

### 4. Caching
- Cache common responses
- Reduce redundant API calls

## Cost Optimization

### Model Selection
- **GPT-4**: More accurate, higher cost
- **GPT-3.5-Turbo**: Faster, lower cost
- Choose based on your needs

### Token Management
- Limit conversation history length
- Use concise system prompts
- Implement token counting

## Next Steps

After completing Phase III:
1. ✅ Chatbot is working locally
2. ➡️ Proceed to **Phase IV**: Deploy to local Kubernetes
3. ➡️ Then **Phase V**: Deploy to cloud with Kafka

## Support

For issues or questions:
- Check logs: `kubectl logs -f <pod-name> -c backend`
- Review OpenAI API status: https://status.openai.com/
- See main deployment guide: `KUBERNETES_DEPLOYMENT.md`
