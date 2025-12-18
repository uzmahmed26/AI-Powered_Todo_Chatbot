# Implementation Plan: Phase III Smart Todo ChatKit App (Integrated System)

**Feature**: 002-smart-todo-chatkit (with integrated components from 003, 004, 005)
**Created**: 2025-12-18
**Status**: Ready for Implementation
**Architecture**: Stateless, MCP-based, AI-powered conversational task management

## Executive Summary

This plan integrates four core components into a cohesive Phase III Smart Todo Chatbot system:
- **Frontend (ChatKit UI)**: OpenAI ChatKit React components (spec 002)
- **Backend (API Layer)**: FastAPI stateless chat endpoint (spec 005)
- **AI Agent (NLU Layer)**: OpenAI Agents SDK with intent recognition (spec 004)
- **MCP Server (Data Layer)**: 5 task management tools via Official MCP SDK (spec 003)
- **Database (Persistence)**: Neon Serverless PostgreSQL with SQLModel ORM (spec 002)

**Integration Architecture**:
```
User → ChatKit UI → FastAPI Endpoint → OpenAI Agent → MCP Tools → Database
  ↑                                         ↓              ↓
  └─────────── Conversation History ────────┴──── Tasks ───┘
```

## System Architecture

### Component Overview

| Component | Technology | Purpose | Spec Reference |
|-----------|-----------|---------|----------------|
| Frontend | OpenAI ChatKit (React/TypeScript) | Conversational UI | 002 |
| Backend API | FastAPI (Python 3.11+) | Stateless chat endpoint | 005 |
| AI Agent | OpenAI Agents SDK + GPT-4 | Intent recognition & tool orchestration | 004 |
| MCP Server | Official MCP SDK (Python) | Task management tools | 003 |
| Database | Neon PostgreSQL + SQLModel | Persistent storage | 002 |
| Auth | Better Auth | User authentication | 002 |

### Data Flow

**User Message Flow**:
1. User types message in ChatKit UI
2. ChatKit sends POST request to `/api/{user_id}/chat`
3. FastAPI endpoint loads conversation history from database
4. FastAPI passes history + message to OpenAI Agent
5. Agent analyzes intent, selects MCP tool (add_task, list_tasks, etc.)
6. Agent invokes MCP tool with extracted parameters
7. MCP tool executes database operation via SQLModel
8. Agent generates natural language response
9. FastAPI stores user + assistant messages to database
10. FastAPI returns response to ChatKit
11. ChatKit displays assistant message

### Database Schema (SQLModel)

**Tables**:
- **tasks**: User tasks (id, user_id, title, description, completed, created_at, updated_at)
- **conversations**: Conversation threads (id, user_id, created_at, updated_at)
- **messages**: Chat messages (id, conversation_id, user_id, role, content, created_at)

**Indexes**:
- tasks(user_id, completed)
- conversations(user_id)
- messages(conversation_id, created_at)

## Implementation Phases

### Phase 1: Foundation & Database

**Objective**: Set up database, models, and MCP server foundation

**Tasks**:
1. **Database Setup** (spec 002, 003)
   - Create Neon Serverless PostgreSQL database
   - Configure connection string and credentials
   - Set up SQLModel engine and session management
   - **Deliverable**: Database connection ready

2. **SQLModel Models** (spec 002)
   - Define Task model (user_id, title, description, completed, timestamps)
   - Define Conversation model (user_id, timestamps)
   - Define Message model (conversation_id, role, content, timestamp)
   - Add relationships and foreign keys
   - **Deliverable**: `models.py` with Task, Conversation, Message models

3. **Database Migrations** (spec 002)
   - Create initial migration (Alembic or SQLModel migrations)
   - Apply migration to Neon database
   - Verify tables and indexes created
   - **Deliverable**: Database schema deployed

4. **MCP Server Skeleton** (spec 003)
   - Install Official MCP SDK
   - Create MCP server project structure
   - Configure server startup and tool registration
   - **Deliverable**: MCP server runs locally

**Acceptance Criteria**:
- ✅ Database accessible with <50ms latency
- ✅ SQLModel models validated (can insert/query)
- ✅ MCP server starts without errors

---

### Phase 2: MCP Tools Implementation

**Objective**: Implement 5 MCP tools for task management (spec 003)

**Tasks**:
1. **add_task Tool** (spec 003)
   - Input: user_id (string), title (string), description (string, optional)
   - Logic: Create new Task in database, return task_id
   - Output: `{success: true, data: {task_id, title, status, created_at}}`
   - Validation: title 1-200 chars, user_id required
   - **Deliverable**: add_task tool callable via MCP

2. **list_tasks Tool** (spec 003)
   - Input: user_id (string), status (string, optional: all/pending/completed)
   - Logic: Query tasks filtered by user_id and status
   - Output: `{success: true, data: {tasks: [...], count}}`
   - **Deliverable**: list_tasks tool returns filtered tasks

3. **complete_task Tool** (spec 003)
   - Input: user_id (string), task_id (integer)
   - Logic: Update task.completed=True, set completed_at timestamp
   - Output: `{success: true, data: {task_id, status: "completed"}}`
   - Validation: Verify task belongs to user_id
   - **Deliverable**: complete_task marks tasks as done

4. **delete_task Tool** (spec 003)
   - Input: user_id (string), task_id (integer)
   - Logic: Soft delete (set status="deleted") or hard delete
   - Output: `{success: true, data: {task_id, deleted: true}}`
   - Validation: Verify task ownership
   - **Deliverable**: delete_task removes tasks

5. **update_task Tool** (spec 003)
   - Input: user_id (string), task_id (integer), title (optional), description (optional)
   - Logic: Update task fields, set updated_at timestamp
   - Output: `{success: true, data: {task_id, title, updated_at}}`
   - **Deliverable**: update_task modifies tasks

6. **Tool Error Handling** (spec 003)
   - Implement validation errors (400-level)
   - Implement authorization errors (403 Forbidden for wrong user_id)
   - Implement not found errors (404)
   - Return consistent JSON error format
   - **Deliverable**: All tools handle errors gracefully

**Acceptance Criteria**:
- ✅ All 5 tools callable via MCP protocol
- ✅ Tools enforce user isolation (403 for wrong user_id)
- ✅ Tools return structured JSON (success/error, data, message)
- ✅ Tool response time <100ms (p95)

---

### Phase 3: OpenAI Agent Integration

**Objective**: Implement AI agent with intent recognition and MCP tool orchestration (spec 004)

**Tasks**:
1. **Agent Initialization** (spec 004)
   - Install OpenAI Agents SDK
   - Configure OpenAI API key (GPT-4)
   - Register MCP tools with agent (function calling)
   - **Deliverable**: Agent can call MCP tools

2. **Intent Recognition** (spec 004)
   - Implement intent mapping (Add → add_task, List → list_tasks, etc.)
   - Define trigger phrases for each intent
   - Test agent with sample inputs
   - **Deliverable**: Agent identifies intents 90%+ accuracy

3. **Parameter Extraction** (spec 004)
   - Extract task title from natural language
   - Extract status filters (pending/completed/all)
   - Extract task references for update/complete/delete
   - Handle missing parameters with clarification prompts
   - **Deliverable**: Agent extracts parameters correctly

4. **Tool Invocation Logic** (spec 004)
   - Agent calls appropriate MCP tool based on intent
   - Pass extracted parameters to MCP tools
   - Handle tool errors and translate to user-friendly messages
   - **Deliverable**: Agent-to-MCP integration working

5. **Response Generation** (spec 004)
   - Generate confirmation messages ("I've added 'buy milk' to your tasks")
   - Format list results (readable task lists)
   - Translate errors to plain language
   - **Deliverable**: Agent responds in natural language

6. **Context Management** (spec 004)
   - Maintain conversation history in agent context
   - Resolve references ("that task", "the report")
   - Limit context to last 20 messages (token limits)
   - **Deliverable**: Agent maintains context across turns

**Acceptance Criteria**:
- ✅ Agent processes natural language inputs successfully
- ✅ Agent calls correct MCP tools 95%+ of the time
- ✅ Agent responses user-friendly (no technical errors)
- ✅ Agent response time <2 seconds (OpenAI API call)

---

### Phase 4: Stateless FastAPI Endpoint

**Objective**: Implement stateless chat API endpoint (spec 005)

**Tasks**:
1. **Endpoint Setup** (spec 005)
   - Create FastAPI project structure
   - Define `POST /api/{user_id}/chat` endpoint
   - Set up request/response models (Pydantic)
   - **Deliverable**: Endpoint accepts requests

2. **Request Validation** (spec 005)
   - Validate user_id from path parameter
   - Validate request body (message required, conversation_id optional)
   - Return 400 Bad Request for invalid inputs
   - **Deliverable**: Input validation working

3. **Conversation Loading** (spec 005)
   - Load conversation by conversation_id from database
   - Verify conversation belongs to user_id (403 if mismatch)
   - Load last 20 messages for context
   - Create new conversation if conversation_id missing
   - **Deliverable**: Conversation history loaded from DB

4. **Message Storage (User)** (spec 005)
   - Store user message to database (role="user", content=message)
   - Use database transaction for atomicity
   - Handle storage failures gracefully
   - **Deliverable**: User messages persisted

5. **Agent Integration** (spec 005)
   - Build agent input (conversation history + new message)
   - Invoke OpenAI Agent with MCP tool access
   - Collect agent response and tool call details
   - Handle agent timeouts (30 seconds)
   - **Deliverable**: Agent processes messages

6. **Message Storage (Assistant)** (spec 005)
   - Store assistant message (role="assistant", content=response)
   - Store tool_calls array (which tools were invoked)
   - Commit transaction
   - **Deliverable**: Assistant messages persisted

7. **Response Formatting** (spec 005)
   - Build JSON response (conversation_id, response, tool_calls)
   - Return 200 OK for success
   - Return appropriate error codes (400, 403, 404, 500, 503, 504)
   - **Deliverable**: Endpoint returns structured responses

8. **Stateless Validation** (spec 005)
   - Ensure zero in-memory conversation state
   - Test server restart mid-conversation (should resume)
   - Test multiple instances with load balancer
   - **Deliverable**: Endpoint fully stateless

**Acceptance Criteria**:
- ✅ Endpoint processes requests in <3 seconds (p95)
- ✅ Conversations persist across server restarts (100%)
- ✅ Endpoint stateless (can scale horizontally)
- ✅ Error handling covers all failure scenarios

---

### Phase 5: OpenAI ChatKit Frontend

**Objective**: Integrate ChatKit UI and connect to backend (spec 002)

**Tasks**:
1. **ChatKit Installation** (spec 002)
   - Install OpenAI ChatKit package (npm/yarn)
   - Set up React project structure
   - Configure ChatKit components
   - **Deliverable**: ChatKit renders in browser

2. **API Integration** (spec 002)
   - Implement API client to call `/api/{user_id}/chat`
   - Handle request/response (send message, receive response)
   - Display assistant responses in ChatKit
   - **Deliverable**: ChatKit communicates with backend

3. **Conversation History Loading** (spec 002)
   - Load conversation history on page load
   - Display past messages in ChatKit
   - Support pagination for long conversations
   - **Deliverable**: Conversation history displays

4. **UI Enhancements** (spec 002)
   - Add typing indicators during agent processing
   - Display message timestamps
   - Show tool call summaries (e.g., "Created task: buy milk")
   - **Deliverable**: ChatKit UX polished

5. **Error Handling** (spec 002)
   - Display user-friendly error messages
   - Handle network failures (retry mechanism)
   - Show loading states
   - **Deliverable**: ChatKit handles errors gracefully

**Acceptance Criteria**:
- ✅ ChatKit displays conversation history correctly
- ✅ User can send messages and receive responses
- ✅ UI responsive and user-friendly
- ✅ Works on modern browsers (Chrome, Firefox, Safari, Edge)

---

### Phase 6: Better Auth Integration

**Objective**: Add authentication and user isolation (spec 002)

**Tasks**:
1. **Better Auth Setup** (spec 002)
   - Install Better Auth library
   - Configure authentication provider
   - Set up user registration/login flows
   - **Deliverable**: Users can authenticate

2. **Frontend Auth Integration** (spec 002)
   - Protect Smart Todo App page (redirect if not authenticated)
   - Display user info in UI
   - Implement logout functionality
   - **Deliverable**: Frontend requires authentication

3. **Backend Auth Integration** (spec 002)
   - Extract user_id from Better Auth session/JWT
   - Validate authentication on all API requests
   - Pass user_id to MCP tools
   - **Deliverable**: Backend enforces authentication

4. **User Isolation Validation** (spec 002)
   - Test user A cannot access user B's conversations
   - Test user A cannot access user B's tasks
   - Verify 403 Forbidden errors for cross-user access
   - **Deliverable**: 100% user isolation enforced

**Acceptance Criteria**:
- ✅ Unauthenticated users redirected to login
- ✅ Authenticated users see only their own data
- ✅ Zero cross-user data leakage

---

### Phase 7: Testing & Validation

**Objective**: Comprehensive testing of integrated system

**Tasks**:
1. **Unit Tests**
   - SQLModel models (Task, Conversation, Message)
   - MCP tools (add_task, list_tasks, complete_task, delete_task, update_task)
   - Agent intent recognition
   - Endpoint request/response handling
   - **Deliverable**: 80%+ code coverage

2. **Integration Tests**
   - End-to-end conversation flow (user message → agent → MCP → response)
   - Conversation persistence and resume
   - Multi-turn conversations with context
   - **Deliverable**: Integration tests passing

3. **Performance Tests**
   - Endpoint latency <3 seconds (p95)
   - Database query latency <100ms
   - Concurrent user load (50 users)
   - **Deliverable**: Performance targets met

4. **Security Tests**
   - User isolation (cross-user access blocked)
   - SQL injection prevention (SQLModel ORM)
   - Authentication bypass attempts
   - **Deliverable**: Security vulnerabilities addressed

5. **User Acceptance Testing**
   - Test with real users (natural language task management)
   - Verify intent recognition accuracy (90%+)
   - Verify conversation context maintained
   - **Deliverable**: UAT feedback incorporated

**Acceptance Criteria**:
- ✅ All tests passing
- ✅ Performance targets met (SC-001 through SC-012)
- ✅ No critical security issues

---

### Phase 8: Deployment

**Objective**: Deploy to production environment

**Tasks**:
1. **Database Deployment**
   - Provision Neon Serverless PostgreSQL production database
   - Apply migrations
   - Configure connection pooling

2. **Backend Deployment**
   - Deploy FastAPI to cloud platform (Render, Railway, AWS Lambda, etc.)
   - Configure environment variables (DB URL, OpenAI API key)
   - Set up auto-scaling and load balancing

3. **MCP Server Deployment**
   - Deploy MCP server (same or separate instance as FastAPI)
   - Configure MCP server endpoint
   - Test MCP tool availability

4. **Frontend Deployment**
   - Build ChatKit UI (production build)
   - Deploy to hosting platform (Vercel, Netlify, Cloudflare Pages)
   - Configure CORS for backend API

5. **Better Auth Production Setup**
   - Configure production auth provider
   - Set up user management
   - Test authentication flow in production

6. **Monitoring & Logging**
   - Set up application logging
   - Configure error tracking (Sentry, Rollbar)
   - Set up performance monitoring
   - Create dashboards for key metrics

**Acceptance Criteria**:
- ✅ System deployed and accessible
- ✅ All components integrated in production
- ✅ Monitoring and logging operational
- ✅ System passes smoke tests in production

---

## Technology Stack Details

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: OpenAI ChatKit
- **Build Tool**: Vite or Create React App
- **HTTP Client**: Axios or Fetch API
- **State Management**: React Context or Zustand (if needed)

### Backend (FastAPI)
- **Framework**: FastAPI 0.100+
- **Python Version**: 3.11+
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic models
- **Middleware**: CORS, authentication, error handling

### AI Agent
- **SDK**: OpenAI Agents SDK (Python)
- **Model**: GPT-4 or GPT-4-Turbo
- **Function Calling**: OpenAI function calling for MCP tools
- **Context Management**: Last 20 messages

### MCP Server
- **SDK**: Official MCP SDK (Python)
- **Tools**: add_task, list_tasks, complete_task, delete_task, update_task
- **Protocol**: MCP over HTTP/JSON

### Database
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Migrations**: Alembic
- **Connection**: asyncpg driver

### Authentication
- **Provider**: Better Auth
- **Method**: Session-based or JWT
- **User Store**: External (Better Auth manages users)

## Integration Points

### Frontend ↔ Backend
- **Protocol**: HTTP/REST
- **Endpoint**: `POST /api/{user_id}/chat`
- **Request**: `{conversation_id?, message}`
- **Response**: `{conversation_id, response, tool_calls}`

### Backend ↔ AI Agent
- **Interface**: Python function calls
- **Input**: Conversation history + new message
- **Output**: Agent response + tool calls

### AI Agent ↔ MCP Server
- **Protocol**: MCP function calling
- **Tools**: 5 task management tools
- **Authentication**: user_id parameter in tool calls

### Backend/MCP ↔ Database
- **ORM**: SQLModel
- **Connection**: Neon PostgreSQL connection string
- **Queries**: Type-safe SQLModel queries

### Backend ↔ Auth Provider
- **Protocol**: Better Auth SDK
- **Purpose**: Extract user_id from session
- **Validation**: Verify authentication on all requests

## Testing Strategy

### Test Pyramid

```
    E2E Tests (10%)
    ─────────────
   Integration Tests (30%)
  ──────────────────────
 Unit Tests (60%)
──────────────────────────
```

**Unit Tests**:
- SQLModel models (serialization, validation)
- MCP tool logic (create, read, update, delete)
- Agent intent recognition (mock OpenAI API)
- Endpoint request validation

**Integration Tests**:
- FastAPI endpoint with database
- Agent with MCP tools
- Conversation persistence and loading
- Multi-turn conversation flows

**E2E Tests**:
- ChatKit UI → Backend → Agent → MCP → Database → Response
- User authentication flow
- Task creation via natural language
- Conversation resume after page reload

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OpenAI API rate limits | High | Implement exponential backoff, caching |
| Neon Serverless cold starts | Medium | Keep database warm, optimize queries |
| MCP tool failures | High | Graceful error handling, retry logic |
| Agent intent accuracy | High | Comprehensive testing, fallback prompts |
| Conversation context limits | Medium | Limit to 20 messages, summarization if needed |
| Better Auth integration issues | Medium | Test early, have fallback auth method |
| Cross-user data leakage | Critical | Rigorous user isolation testing |
| Stateless architecture failures | High | Test server restarts, load balancing |

## Success Metrics (from spec 002)

- **SC-001**: Users create todos using natural language with 90%+ success rate
- **SC-002**: 100% of CRUD operations via MCP tools (no direct DB access)
- **SC-003**: 100% conversation persistence across server restarts
- **SC-004**: Conversation history loads in <1 second (p95)
- **SC-005**: AI agent responds in <3 seconds (p95)
- **SC-006**: 100% conversation resume after browser reload
- **SC-007**: Stateless architecture validated (multiple instances)
- **SC-008**: 100% user isolation (Better Auth)
- **SC-009**: 0% technical jargon in error messages
- **SC-010**: ChatKit displays typing indicators and status
- **SC-011**: 50 concurrent users supported without degradation
- **SC-012**: Neon cold start <2 seconds

## Next Steps

1. **Phase 1 Start**: Set up Neon database and SQLModel models
2. **Create Tasks**: Use `/sp.tasks` to break down phases into atomic tasks
3. **Begin Implementation**: Use `/sp.implement` for TDD approach
4. **Iterative Development**: Complete one phase at a time, validate before moving forward
5. **Continuous Testing**: Write tests alongside implementation (TDD)
6. **Deployment**: Deploy after Phase 7 (Testing) completes successfully

---

**Plan Status**: ✅ Ready for Task Generation (`/sp.tasks`)
**Implementation Approach**: Phased, with clear deliverables and acceptance criteria
**Estimated Timeline**: 8 phases, each phase 3-7 days (total 24-56 days for full implementation)
