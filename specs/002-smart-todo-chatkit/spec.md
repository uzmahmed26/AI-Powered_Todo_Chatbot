# Feature Specification: Smart Todo ChatKit App

**Feature Branch**: `002-smart-todo-chatkit`
**Created**: 2025-12-17
**Status**: Draft
**Input**: User description: "Phase III Smart Todo Chatbot with OpenAI ChatKit UI, OpenAI Agents SDK, Official MCP SDK, SQLModel ORM, Neon Serverless PostgreSQL, Better Auth. Stateless FastAPI endpoint. Only Smart Todo App page, not global."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Todo Creation (Priority: P1)

Users create todo items through OpenAI ChatKit interface using natural language without specific command syntax.

**Why this priority**: Core MVP - validates entire AI + MCP integration stack.

**Independent Test**: Type "Remind me to buy groceries tomorrow" in ChatKit, verify todo created in database via MCP tool.

**Acceptance Scenarios**:

1. **Given** user opens Smart Todo App with ChatKit, **When** user types "Add task: finish report by Friday", **Then** OpenAI agent extracts intent, calls MCP create_todo tool with title "finish report" and due_date next Friday
2. **Given** authenticated user, **When** user types "I need to call mom tomorrow at 3pm", **Then** system creates todo via MCP with due_date tomorrow, due_time 15:00
3. **Given** user types "buy milk", **When** agent processes, **Then** MCP tool creates todo with title "buy milk", no due date
4. **Given** conversation context exists, **When** user types "Also buy bread", **Then** system creates second todo using conversation context

---

### User Story 2 - Todo CRUD via Chat (Priority: P1)

Users perform view, update, complete, delete operations through natural conversation using OpenAI Agents SDK with MCP tool calls.

**Why this priority**: Completes MVP - full task list control through chat.

**Independent Test**: Create todo, then use natural language to list, update, complete, delete via ChatKit.

**Acceptance Scenarios**:

1. **Given** user has todos, **When** types "show my tasks", **Then** agent calls MCP list_todos, displays formatted results in ChatKit
2. **Given** todo "buy groceries" exists, **When** types "mark buy groceries done", **Then** agent calls MCP complete_todo, confirms action
3. **Given** todo "meeting at 2pm", **When** types "change meeting to 3pm", **Then** agent calls MCP update_todo for due_time
4. **Given** todo "old task", **When** types "delete old task", **Then** agent calls MCP delete_todo (soft delete)
5. **Given** user asks "what's due today", **When** processed, **Then** MCP list_todos filters by due_date=today

---

### User Story 3 - Conversation Persistence & Resume (Priority: P1)

Conversations persist in Neon PostgreSQL, resume after server restart with full context maintained.

**Why this priority**: Core requirement - stateless architecture validation.

**Independent Test**: Create conversation, restart FastAPI, reload page, verify history displays and context maintained.

**Acceptance Scenarios**:

1. **Given** conversation with 10 messages, **When** user closes/reopens browser, **Then** ChatKit loads full history from database
2. **Given** FastAPI restart, **When** user sends message, **Then** agent loads conversation from database, maintains context
3. **Given** todo created in previous conversation, **When** user refers to "that task" later, **Then** agent retrieves context, identifies correct todo
4. **Given** conversation has 100+ messages, **When** loaded, **Then** system loads last 20 initially (pagination)

---

### User Story 4 - Authentication with Better Auth (Priority: P2)

Users authenticate with Better Auth before accessing Smart Todo App. Todos are user-isolated.

**Why this priority**: Security and user isolation critical.

**Independent Test**: Access Smart Todo App without auth (redirect to login), login, verify access and user-specific todos.

**Acceptance Scenarios**:

1. **Given** unauthenticated user, **When** navigates to Smart Todo App, **Then** Better Auth redirects to login
2. **Given** user logs in via Better Auth, **When** succeeds, **Then** redirected to Smart Todo App with ChatKit
3. **Given** authenticated user creates todos, **When** saved, **Then** todos associated with user_id from Better Auth
4. **Given** two users logged in separately, **When** each creates todos, **Then** users see only their own todos (MCP enforces isolation)

---

### User Story 5 - Stateless FastAPI Endpoint (Priority: P2)

FastAPI chat endpoint is stateless - all conversation state persists in Neon database for horizontal scaling.

**Why this priority**: Architectural requirement - stateless design enables cloud deployment.

**Independent Test**: Send message, verify response, restart FastAPI, send follow-up, verify continuity from database.

**Acceptance Scenarios**:

1. **Given** FastAPI receives chat message, **When** processing completes, **Then** conversation persisted to Neon before response
2. **Given** FastAPI crashes mid-conversation, **When** restarts and user sends message, **Then** conversation resumes from database with context
3. **Given** multiple FastAPI instances load-balanced, **When** messages hit different instances, **Then** all load from shared Neon database (stateless)
4. **Given** conversation in database, **When** OpenAI agent needs context, **Then** loads last N messages from database (no in-memory cache)

---

### Edge Cases

- What if OpenAI Agents SDK API unavailable or times out?
- How to handle unparseable natural language?
- What if MCP tool call fails (database down)?
- How to handle 1000+ message conversations?
- What if rapid messages sent before responses complete?
- How does Better Auth handle session expiration during chat?
- What if duplicate todos (same title, due date)?
- How to handle timezone differences?
- What if Neon Serverless scales to zero (cold start)?
- How to handle concurrent todo updates from multiple devices?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST use OpenAI ChatKit for UI on Smart Todo App page only
- **FR-002**: System MUST implement stateless FastAPI chat endpoint POST /api/chat
- **FR-003**: System MUST use OpenAI Agents SDK for NLU and intent extraction
- **FR-004**: System MUST use Official MCP SDK for tool-based todo operations
- **FR-005**: System MUST persist conversations in Neon Serverless PostgreSQL
- **FR-006**: System MUST resume conversations after server restart from database
- **FR-007**: System MUST use SQLModel ORM for type-safe database operations
- **FR-008**: System MUST use Better Auth for authentication and session management
- **FR-009**: System MUST scope todos to authenticated user_id from Better Auth
- **FR-010**: System MUST maintain zero in-memory conversation state (load from DB each request)
- **FR-011**: MCP tools MUST be registered with OpenAI agent for function calling
- **FR-012**: MCP tools MUST include: create_todo, list_todos, get_todo, update_todo, delete_todo, complete_todo
- **FR-013**: System MUST support flexible date/time parsing (tomorrow, next Friday, in 3 days)
- **FR-014**: System MUST provide user-friendly error messages (no stack traces)
- **FR-015**: System MUST validate input at API boundary (Pydantic models)
- **FR-016**: System MUST log all AI interactions and MCP tool calls
- **FR-017**: System MUST handle OpenAI API rate limits with exponential backoff
- **FR-018**: ChatKit MUST display conversation history on page load
- **FR-019**: ChatKit MUST show loading indicators during AI processing
- **FR-020**: System MUST support pagination for conversations >50 messages

### Key Entities

**SQLModel Database Schema** (Stateless Chat Flow Support):

**Task Model**:
- `user_id`: string (FK to Better Auth users)
- `id`: integer (primary key, auto-increment)
- `title`: string (required, max 200 chars)
- `description`: string (optional, nullable)
- `completed`: boolean (default False)
- `created_at`: datetime (auto-generated)
- `updated_at`: datetime (auto-updated)

**Conversation Model**:
- `user_id`: string (FK to Better Auth users)
- `id`: integer (primary key, auto-increment)
- `created_at`: datetime (auto-generated)
- `updated_at`: datetime (auto-updated)

**Message Model**:
- `user_id`: string (FK to Better Auth users, for direct user queries)
- `id`: integer (primary key, auto-increment)
- `conversation_id`: integer (FK to Conversation.id, ON DELETE CASCADE)
- `role`: enum ("user", "assistant") - message sender type
- `content`: text (message content, unlimited length)
- `created_at`: datetime (auto-generated)

**Relationships**:
- Conversation → Messages: One-to-Many (a conversation has many messages)
- User (Better Auth) → Tasks: One-to-Many (a user has many tasks)
- User (Better Auth) → Conversations: One-to-Many (a user has many conversations)
- User (Better Auth) → Messages: One-to-Many (for direct queries)

**Indexes** (for stateless performance):
- `Task.user_id` - fast user-specific task retrieval
- `Task.completed` - filter active vs completed tasks
- `Conversation.user_id` - fast user-specific conversation retrieval
- `Message.conversation_id` - fast message retrieval for conversation history
- `Message.created_at` - chronological ordering

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users create todos using natural language in ChatKit with 90%+ success rate (agent parses intent correctly)
- **SC-002**: Users perform all CRUD operations via chat without direct database access (100% via MCP tools)
- **SC-003**: Conversations persist across server restarts with 100% reliability (no data loss)
- **SC-004**: System loads conversation history in under 1 second for <100 message conversations (p95)
- **SC-005**: AI agent responds to chat messages in under 3 seconds (p95, includes OpenAI API + MCP calls)
- **SC-006**: Users resume conversations after browser reload with full context (100%)
- **SC-007**: Multiple FastAPI instances serve same user without state conflicts (stateless validation)
- **SC-008**: Better Auth prevents unauthorized todo access (100% user isolation)
- **SC-009**: System handles OpenAI API failures gracefully with user-friendly messages (0% technical jargon)
- **SC-010**: ChatKit displays real-time typing indicators and message status
- **SC-011**: System supports 50 concurrent users on single FastAPI instance without degradation (<3s response)
- **SC-012**: Neon Serverless cold start completes in under 2 seconds (user perceives <5s total)

### Assumptions

- OpenAI Agents SDK compatible with FastAPI Python async
- Official MCP SDK supports Python, integrates with OpenAI Agents SDK for tool registration
- OpenAI ChatKit provides React/TypeScript components embeddable in Smart Todo App page
- Better Auth supports required authentication flow (session or JWT)
- Neon Serverless PostgreSQL provides <100ms query latency for real-time chat
- Users access via modern browsers (Chrome, Firefox, Safari, Edge latest)
- FastAPI and frontend deployed together or CORS configured properly
- OpenAI API key available for Agents SDK (GPT-4 or GPT-3.5-turbo)
- Average conversation size 10-50 messages (1-5 KB)
- Primary language: English (multi-language not required for MVP)

### Out of Scope

- Global chatbot across entire application (only Smart Todo App page)
- Team/shared todos
- Calendar integration
- Recurring todos with complex rules
- File attachments
- Subtasks or hierarchical structures
- Time tracking, pomodoro timer
- Native mobile apps (web-only MVP)
- Email/push notifications
- Import/export from other todo apps
- Offline support
- Voice input/output (text-only MVP)
- Custom AI model training

### Dependencies

- OpenAI ChatKit (React/TypeScript)
- FastAPI framework (Python 3.11+)
- OpenAI Agents SDK + OpenAI API
- Official MCP SDK (Python)
- SQLModel ORM
- Neon Serverless PostgreSQL
- Better Auth
- Cloud hosting (Vercel, Railway, Render, AWS Lambda, etc.)

### Non-Functional Requirements

- **Performance**: Chat responses <3s (p95), conversation load <1s, database queries <100ms
- **Scalability**: Stateless architecture enables horizontal scaling, Neon auto-scales
- **Reliability**: 99.5% uptime, graceful degradation if OpenAI API unavailable
- **Security**: Better Auth handles authentication, Pydantic input validation, SQLModel prevents SQL injection, CORS configured, HTTPS in production
- **Privacy**: User isolation (todos scoped to user_id), conversation data encrypted at rest (Neon default)
- **Observability**: Structured JSON logging, request tracing, OpenAI API metrics, MCP tool call logging
- **Maintainability**: Type-safe code (Pydantic, SQLModel), clear separation of concerns, comprehensive error handling
- **Usability**: ChatKit modern UX (typing indicators, message bubbles, timestamps), user-friendly errors

## Workflow Example

**User**: "Remind me to buy milk tomorrow"

1. ChatKit sends message to FastAPI `/api/chat`
2. FastAPI authenticates (Better Auth session)
3. FastAPI loads conversation from Neon (if conversation_id provided)
4. FastAPI initializes OpenAI Agent with conversation history
5. OpenAI Agent processes: extracts intent (create_todo), entities (title="buy milk", due_date="tomorrow" → 2025-12-18)
6. OpenAI Agent calls MCP tool: `create_todo(title="buy milk", due_date="2025-12-18")`
7. MCP tool executes SQLModel query, inserts todo in Neon
8. MCP tool returns success with todo_id
9. OpenAI Agent generates response: "✓ Added 'buy milk' to your tasks for tomorrow (Dec 18)"
10. FastAPI appends user + assistant messages to conversation in database
11. FastAPI returns response to ChatKit
12. ChatKit displays assistant message

## Next Steps

1. ✅ **Specification Complete**
2. ⏭️ `/sp.plan` - Architecture, MCP SDK integration, SQLModel schema, FastAPI structure, OpenAI Agent config
3. ⏭️ `/sp.tasks` - Atomic tasks with file paths and test requirements
4. ⏭️ `/sp.implement` - Autonomous TDD implementation
5. ⏭️ Testing & Deployment - Integration tests, E2E tests, cloud deployment
