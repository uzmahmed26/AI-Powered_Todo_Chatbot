# Tasks: Phase III Smart Todo ChatKit App (Integrated System)

**Input**: Design documents from `specs/002-smart-todo-chatkit/`
**Prerequisites**: plan.md (integrated 8-phase plan), spec.md (5 user stories P1-P2)

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are omitted per the template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

This project follows a web app structure:
- **Backend**: `backend/` (FastAPI, MCP Server, AI Agent)
- **Frontend**: `frontend/` (React, TypeScript, OpenAI ChatKit)
- **Database**: Neon Serverless PostgreSQL (cloud-hosted)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the integrated system

- [X] T001 Create project directory structure (backend/, frontend/, docs/)
- [X] T002 [P] Initialize Python backend project with FastAPI, SQLModel, OpenAI SDK, MCP SDK in backend/pyproject.toml
- [X] T003 [P] Initialize React frontend project with TypeScript, OpenAI ChatKit, Axios in frontend/package.json
- [X] T004 [P] Configure Python linting (black, ruff, mypy) in backend/pyproject.toml
- [X] T005 [P] Configure TypeScript linting (ESLint, Prettier) in frontend/.eslintrc.json
- [X] T006 Create environment configuration template in backend/.env.example (DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET)
- [X] T007 [P] Create frontend environment template in frontend/.env.example (VITE_API_URL, VITE_BETTER_AUTH_URL)
- [X] T008 Set up Git repository with .gitignore for Python and Node.js in .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Foundation

- [ ] T009 Create Neon Serverless PostgreSQL database and obtain connection string
- [X] T010 Configure SQLModel database engine and session management in backend/src/database/engine.py
- [X] T011 [P] Define Task SQLModel in backend/src/models/task.py (user_id, id, title, description, completed, created_at, updated_at)
- [X] T012 [P] Define Conversation SQLModel in backend/src/models/conversation.py (user_id, id, created_at, updated_at)
- [X] T013 [P] Define Message SQLModel in backend/src/models/message.py (user_id, id, conversation_id, role, content, created_at)
- [X] T014 Create database migration script using Alembic in backend/alembic/versions/001_initial_schema.py
- [ ] T015 Apply database migration to Neon PostgreSQL and verify tables created
- [X] T016 [P] Create database indexes (task.user_id, task.completed, conversation.user_id, message.conversation_id, message.created_at) in migration

### MCP Server Foundation

- [X] T017 Install Official MCP SDK in backend/requirements.txt
- [X] T018 Create MCP server project structure in backend/src/mcp_server/
- [X] T019 Configure MCP server startup and tool registration in backend/src/mcp_server/server.py
- [X] T020 Define MCP tool schemas (add_task, list_tasks, complete_task, delete_task, update_task) in backend/src/mcp_server/schemas.py

### AI Agent Foundation

- [X] T021 Install OpenAI Agents SDK in backend/requirements.txt
- [X] T022 Create agent initialization module in backend/src/agent/agent.py
- [X] T023 Configure OpenAI API client (GPT-4) in backend/src/agent/client.py
- [X] T024 Register MCP tools with OpenAI agent for function calling in backend/src/agent/tool_registry.py

### API Foundation

- [X] T025 Create FastAPI application structure in backend/src/api/app.py
- [X] T026 [P] Configure CORS middleware for frontend in backend/src/api/middleware/cors.py
- [X] T027 [P] Configure error handling middleware in backend/src/api/middleware/error_handler.py
- [X] T028 [P] Configure logging middleware in backend/src/api/middleware/logging.py
- [X] T029 Define Pydantic request/response models in backend/src/api/models.py (ChatRequest, ChatResponse)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Todo Creation (Priority: P1) 🎯 MVP

**Goal**: Users create todo items through OpenAI ChatKit interface using natural language without specific command syntax

**Independent Test**: Type "Remind me to buy groceries tomorrow" in ChatKit, verify todo created in database via MCP tool

**Reference**: spec.md User Story 1 (lines 10-24)

### Implementation for User Story 1

#### MCP Tool: add_task

- [X] T030 [P] [US1] Implement add_task MCP tool in backend/src/mcp_server/tools/add_task.py
- [X] T031 [US1] Add input validation for add_task (title 1-200 chars, user_id required) in backend/src/mcp_server/tools/add_task.py
- [X] T032 [US1] Implement database insert logic for Task model in backend/src/mcp_server/tools/add_task.py
- [X] T033 [US1] Add error handling for add_task (400 validation, 403 authorization, 500 database) in backend/src/mcp_server/tools/add_task.py
- [X] T034 [US1] Format add_task success response (task_id, title, status, created_at) in backend/src/mcp_server/tools/add_task.py

#### AI Agent: Intent Recognition & Parameter Extraction

- [X] T035 [P] [US1] Implement intent detection for "Add" intent in backend/src/agent/intents.py
- [X] T036 [US1] Define trigger phrases for Add intent ("add task", "remind me", "create", "I need to") in backend/src/agent/intents.py
- [X] T037 [US1] Implement parameter extraction for task title in backend/src/agent/extractors.py
- [X] T038 [P] [US1] Implement natural language date parsing ("tomorrow", "next Friday", "in 3 days") in backend/src/agent/date_parser.py
- [X] T039 [US1] Implement clarification prompt logic for missing task title in backend/src/agent/clarifiers.py
- [X] T040 [US1] Implement agent response generation for successful task creation in backend/src/agent/responses.py

#### FastAPI Endpoint Integration

- [X] T041 [US1] Implement POST /api/{user_id}/chat endpoint handler in backend/src/api/routes/chat.py
- [X] T042 [US1] Add request validation (user_id from path, message from body) in backend/src/api/routes/chat.py
- [X] T043 [US1] Implement conversation loading from database in backend/src/api/services/conversation_service.py
- [X] T044 [US1] Implement user message storage (role="user") in backend/src/api/services/message_service.py
- [X] T045 [US1] Implement agent invocation with conversation history in backend/src/api/services/chat_service.py
- [X] T046 [US1] Implement assistant message storage (role="assistant", tool_calls) in backend/src/api/services/message_service.py
- [X] T047 [US1] Implement response formatting (conversation_id, response, tool_calls) in backend/src/api/routes/chat.py

#### ChatKit Frontend

- [X] T048 [P] [US1] Install OpenAI ChatKit package in frontend/package.json
- [X] T049 [P] [US1] Create Smart Todo App page component in frontend/src/pages/SmartTodoApp.tsx
- [X] T050 [US1] Configure ChatKit component in frontend/src/pages/SmartTodoApp.tsx
- [X] T051 [US1] Implement API client for POST /api/{user_id}/chat in frontend/src/services/api.ts
- [X] T052 [US1] Implement send message handler in frontend/src/pages/SmartTodoApp.tsx
- [X] T053 [US1] Display assistant responses in ChatKit in frontend/src/pages/SmartTodoApp.tsx
- [X] T054 [P] [US1] Add typing indicator during agent processing in frontend/src/pages/SmartTodoApp.tsx
- [X] T055 [P] [US1] Add error message display in ChatKit in frontend/src/pages/SmartTodoApp.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create todos using natural language

---

## Phase 4: User Story 2 - Todo CRUD via Chat (Priority: P1)

**Goal**: Users perform view, update, complete, delete operations through natural conversation using OpenAI Agents SDK with MCP tool calls

**Independent Test**: Create todo, then use natural language to list, update, complete, delete via ChatKit

**Reference**: spec.md User Story 2 (lines 27-42)

### Implementation for User Story 2

#### MCP Tools: list_tasks, complete_task, delete_task, update_task

- [ ] T056 [P] [US2] Implement list_tasks MCP tool in backend/src/mcp_server/tools/list_tasks.py
- [ ] T057 [P] [US2] Implement complete_task MCP tool in backend/src/mcp_server/tools/complete_task.py
- [ ] T058 [P] [US2] Implement delete_task MCP tool in backend/src/mcp_server/tools/delete_task.py
- [ ] T059 [P] [US2] Implement update_task MCP tool in backend/src/mcp_server/tools/update_task.py
- [ ] T060 [US2] Add status filtering for list_tasks (all/pending/completed) in backend/src/mcp_server/tools/list_tasks.py
- [ ] T061 [US2] Add task ownership validation for complete_task (403 if wrong user_id) in backend/src/mcp_server/tools/complete_task.py
- [ ] T062 [US2] Add task ownership validation for delete_task (403 if wrong user_id) in backend/src/mcp_server/tools/delete_task.py
- [ ] T063 [US2] Add task ownership validation for update_task (403 if wrong user_id) in backend/src/mcp_server/tools/update_task.py
- [ ] T064 [US2] Implement soft delete logic (set deleted flag) in backend/src/mcp_server/tools/delete_task.py
- [ ] T065 [US2] Add 404 error handling for task not found in all CRUD tools in backend/src/mcp_server/tools/

#### AI Agent: Intent Recognition for CRUD Operations

- [ ] T066 [P] [US2] Implement intent detection for "List" intent in backend/src/agent/intents.py
- [ ] T067 [P] [US2] Implement intent detection for "Complete" intent in backend/src/agent/intents.py
- [ ] T068 [P] [US2] Implement intent detection for "Delete" intent in backend/src/agent/intents.py
- [ ] T069 [P] [US2] Implement intent detection for "Update" intent in backend/src/agent/intents.py
- [ ] T070 [US2] Define trigger phrases for List intent ("show my tasks", "what's due today", "list todos") in backend/src/agent/intents.py
- [ ] T071 [US2] Define trigger phrases for Complete intent ("mark done", "complete task", "finish") in backend/src/agent/intents.py
- [ ] T072 [US2] Define trigger phrases for Delete intent ("delete task", "remove", "get rid of") in backend/src/agent/intents.py
- [ ] T073 [US2] Define trigger phrases for Update intent ("change", "update", "modify") in backend/src/agent/intents.py
- [ ] T074 [US2] Implement parameter extraction for status filter in backend/src/agent/extractors.py
- [ ] T075 [US2] Implement task reference resolution ("buy groceries", "that task") in backend/src/agent/extractors.py
- [ ] T076 [US2] Implement agent response generation for list results (formatted task lists) in backend/src/agent/responses.py
- [ ] T077 [US2] Implement agent response generation for complete/delete/update confirmations in backend/src/agent/responses.py

#### Frontend Enhancements

- [ ] T078 [P] [US2] Add tool call summary display in ChatKit ("Created task: buy milk") in frontend/src/components/ToolCallSummary.tsx
- [ ] T079 [US2] Integrate tool call summary into ChatKit messages in frontend/src/pages/SmartTodoApp.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full CRUD via chat

---

## Phase 5: User Story 3 - Conversation Persistence & Resume (Priority: P1)

**Goal**: Conversations persist in Neon PostgreSQL, resume after server restart with full context maintained

**Independent Test**: Create conversation, restart FastAPI, reload page, verify history displays and context maintained

**Reference**: spec.md User Story 3 (lines 45-59)

### Implementation for User Story 3

#### Conversation & Message Persistence

- [ ] T080 [P] [US3] Implement conversation creation service in backend/src/api/services/conversation_service.py
- [ ] T081 [US3] Implement conversation retrieval by ID in backend/src/api/services/conversation_service.py
- [ ] T082 [US3] Implement conversation ownership validation (403 if user_id mismatch) in backend/src/api/services/conversation_service.py
- [ ] T083 [US3] Implement message batch loading (last 20 messages) in backend/src/api/services/message_service.py
- [ ] T084 [P] [US3] Add database transaction management for message storage in backend/src/api/services/message_service.py
- [ ] T085 [US3] Implement rollback on agent failure in backend/src/api/services/chat_service.py

#### Stateless Architecture Enforcement

- [ ] T086 [US3] Remove all in-memory conversation state from FastAPI app in backend/src/api/app.py
- [ ] T087 [US3] Implement conversation history loading on every request in backend/src/api/routes/chat.py
- [ ] T088 [US3] Add stateless validation test (server restart mid-conversation) in backend/tests/test_stateless.py

#### Frontend Conversation History

- [ ] T089 [P] [US3] Implement conversation history loading on page load in frontend/src/services/api.ts
- [ ] T090 [US3] Display past messages in ChatKit on component mount in frontend/src/pages/SmartTodoApp.tsx
- [ ] T091 [P] [US3] Implement pagination for conversations >50 messages in frontend/src/pages/SmartTodoApp.tsx
- [ ] T092 [US3] Persist conversation_id in browser localStorage in frontend/src/pages/SmartTodoApp.tsx
- [ ] T093 [US3] Resume conversation on page reload using stored conversation_id in frontend/src/pages/SmartTodoApp.tsx

#### Agent Context Management

- [ ] T094 [US3] Implement context loading (last 20 messages) in agent in backend/src/agent/context.py
- [ ] T095 [US3] Implement reference resolution using conversation context ("that task") in backend/src/agent/extractors.py
- [ ] T096 [US3] Add context truncation for token limit management in backend/src/agent/context.py

**Checkpoint**: All user stories (1, 2, 3) should now work with full conversation persistence

---

## Phase 6: User Story 4 - Authentication with Better Auth (Priority: P2)

**Goal**: Users authenticate with Better Auth before accessing Smart Todo App. Todos are user-isolated.

**Independent Test**: Access Smart Todo App without auth (redirect to login), login, verify access and user-specific todos

**Reference**: spec.md User Story 4 (lines 62-76)

### Implementation for User Story 4

#### Better Auth Setup

- [ ] T097 [P] [US4] Install Better Auth library in backend/requirements.txt and frontend/package.json
- [ ] T098 [US4] Configure Better Auth provider in backend/src/auth/config.py
- [ ] T099 [P] [US4] Set up user registration flow in backend/src/auth/routes.py
- [ ] T100 [P] [US4] Set up login flow in backend/src/auth/routes.py
- [ ] T101 [P] [US4] Set up logout flow in backend/src/auth/routes.py

#### Backend Authentication Integration

- [ ] T102 [US4] Implement authentication middleware for API routes in backend/src/api/middleware/auth.py
- [ ] T103 [US4] Implement user_id extraction from Better Auth session/JWT in backend/src/api/middleware/auth.py
- [ ] T104 [US4] Add authentication validation on POST /api/{user_id}/chat in backend/src/api/routes/chat.py
- [ ] T105 [US4] Verify user_id from path matches authenticated user_id (403 if mismatch) in backend/src/api/routes/chat.py
- [ ] T106 [US4] Pass authenticated user_id to MCP tools in backend/src/api/services/chat_service.py

#### Frontend Authentication Integration

- [ ] T107 [US4] Implement authentication check on Smart Todo App page in frontend/src/pages/SmartTodoApp.tsx
- [ ] T108 [US4] Redirect unauthenticated users to login page in frontend/src/pages/SmartTodoApp.tsx
- [ ] T109 [P] [US4] Display user info in UI header in frontend/src/components/UserHeader.tsx
- [ ] T110 [P] [US4] Implement logout button in frontend/src/components/UserHeader.tsx
- [ ] T111 [US4] Include Better Auth token in API requests in frontend/src/services/api.ts

#### User Isolation Validation

- [ ] T112 [US4] Enforce user_id filtering in all MCP tools in backend/src/mcp_server/tools/
- [ ] T113 [US4] Add user isolation test (user A cannot access user B's tasks) in backend/tests/test_user_isolation.py
- [ ] T114 [US4] Add user isolation test (user A cannot access user B's conversations) in backend/tests/test_user_isolation.py
- [ ] T115 [US4] Verify 403 Forbidden errors for cross-user access attempts in backend/tests/test_user_isolation.py

**Checkpoint**: Authentication and user isolation complete - system is secure

---

## Phase 7: User Story 5 - Stateless FastAPI Endpoint (Priority: P2)

**Goal**: FastAPI chat endpoint is stateless - all conversation state persists in Neon database for horizontal scaling

**Independent Test**: Send message, verify response, restart FastAPI, send follow-up, verify continuity from database

**Reference**: spec.md User Story 5 (lines 79-93)

### Implementation for User Story 5

#### Stateless Architecture Validation

- [ ] T116 [US5] Audit FastAPI app for in-memory state (remove global variables) in backend/src/api/app.py
- [ ] T117 [US5] Ensure all conversation data loaded from database on each request in backend/src/api/routes/chat.py
- [ ] T118 [US5] Ensure agent context loaded from database (no caching) in backend/src/agent/context.py
- [ ] T119 [US5] Implement database connection pooling for concurrent requests in backend/src/database/engine.py

#### Horizontal Scaling Tests

- [ ] T120 [P] [US5] Create test for server restart mid-conversation in backend/tests/test_stateless.py
- [ ] T121 [P] [US5] Create test for load balancing across multiple instances in backend/tests/test_stateless.py
- [ ] T122 [US5] Verify conversation continuity after FastAPI restart in backend/tests/test_stateless.py
- [ ] T123 [US5] Verify no state conflicts when messages hit different instances in backend/tests/test_stateless.py

#### Performance Optimization

- [ ] T124 [P] [US5] Add database query optimization (index usage verification) in backend/src/database/queries.py
- [ ] T125 [P] [US5] Implement efficient conversation history pagination in backend/src/api/services/message_service.py
- [ ] T126 [US5] Add request timeout handling (30 seconds) in backend/src/api/middleware/timeout.py
- [ ] T127 [US5] Implement database connection retry logic in backend/src/database/engine.py

#### Error Handling & Resilience

- [ ] T128 [P] [US5] Implement graceful degradation for OpenAI API failures in backend/src/agent/client.py
- [ ] T129 [P] [US5] Implement exponential backoff for OpenAI rate limits in backend/src/agent/client.py
- [ ] T130 [US5] Add user-friendly error messages (no stack traces) in backend/src/api/middleware/error_handler.py
- [ ] T131 [US5] Implement database failure error handling in backend/src/api/services/chat_service.py

**Checkpoint**: System is fully stateless and horizontally scalable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Frontend Polish

- [ ] T132 [P] Add message timestamps display in frontend/src/components/MessageTimestamp.tsx
- [ ] T133 [P] Add loading states for all async operations in frontend/src/pages/SmartTodoApp.tsx
- [ ] T134 [P] Implement retry mechanism for network failures in frontend/src/services/api.ts
- [ ] T135 Add responsive design for mobile browsers in frontend/src/pages/SmartTodoApp.tsx
- [ ] T136 [P] Add accessibility features (ARIA labels, keyboard navigation) in frontend/src/pages/SmartTodoApp.tsx

### Backend Polish

- [ ] T137 [P] Implement structured JSON logging in backend/src/api/middleware/logging.py
- [ ] T138 [P] Add request tracing with correlation IDs in backend/src/api/middleware/logging.py
- [ ] T139 [P] Add OpenAI API metrics logging in backend/src/agent/client.py
- [ ] T140 [P] Add MCP tool call logging in backend/src/mcp_server/server.py
- [ ] T141 Add comprehensive error taxonomy in backend/src/api/errors.py

### Security Hardening

- [ ] T142 [P] Configure HTTPS in production (SSL certificates) in deployment config
- [ ] T143 [P] Implement rate limiting on API endpoints in backend/src/api/middleware/rate_limit.py
- [ ] T144 [P] Add input sanitization for all user inputs in backend/src/api/validators.py
- [ ] T145 Verify SQL injection prevention (SQLModel ORM) in backend/tests/test_security.py
- [ ] T146 [P] Add CORS whitelist configuration in backend/src/api/middleware/cors.py

### Deployment Preparation

- [ ] T147 [P] Create Docker image for FastAPI backend in backend/Dockerfile
- [ ] T148 [P] Create production build configuration for frontend in frontend/vite.config.ts
- [ ] T149 [P] Set up environment variable management in .env.production
- [ ] T150 Create deployment documentation in docs/deployment.md
- [ ] T151 [P] Configure monitoring and alerting (Sentry, Rollbar) in backend/src/monitoring/
- [ ] T152 [P] Create health check endpoint GET /health in backend/src/api/routes/health.py

### Documentation

- [ ] T153 [P] Create API documentation (OpenAPI/Swagger) in backend/src/api/docs.py
- [ ] T154 [P] Create developer setup guide in docs/setup.md
- [ ] T155 [P] Create user guide for Smart Todo App in docs/user-guide.md
- [ ] T156 Document MCP tool schemas in docs/mcp-tools.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1) - Can start after Phase 2
  - User Story 2 (P1) - Can start after Phase 2 (integrates with US1)
  - User Story 3 (P1) - Can start after Phase 2 (enhances US1+US2)
  - User Story 4 (P2) - Can start after Phase 2 (secures all stories)
  - User Story 5 (P2) - Can start after Phase 2 (validates architecture)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Builds on US1 (add_task tool)
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Enhances US1+US2 with persistence
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Secures all stories, should be done before production
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Validates stateless architecture for all stories

### Within Each User Story

- Foundation tasks (T009-T029) MUST complete before any user story
- MCP tools before agent integration
- Agent integration before API endpoints
- API endpoints before frontend integration
- Core implementation before polish

### Parallel Opportunities

- **Setup Phase**: T002-T007 can run in parallel (backend setup, frontend setup, configs)
- **Foundational Phase**:
  - Models (T011-T013) can run in parallel
  - Foundation modules (T026-T028) can run in parallel
- **User Story 1**:
  - T030 (add_task tool), T035 (intent detection), T048 (ChatKit install) can run in parallel
  - T054 (typing indicator), T055 (error display) can run in parallel
- **User Story 2**:
  - All 4 MCP tools (T056-T059) can run in parallel
  - All 4 intent detections (T066-T069) can run in parallel
- **User Story 3**:
  - T080 (conversation creation), T089 (history loading) can run in parallel
  - T091 (pagination), T092 (localStorage) can run in parallel
- **User Story 4**:
  - T099-T101 (auth flows) can run in parallel
  - T109 (user header), T110 (logout button) can run in parallel
- **User Story 5**:
  - T120 (restart test), T121 (load balance test) can run in parallel
  - T124 (query optimization), T125 (pagination) can run in parallel
  - T128 (API failures), T129 (rate limits) can run in parallel
- **Polish Phase**:
  - Most polish tasks (T132-T156) can run in parallel as they affect different files

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool, intent detection, and ChatKit install in parallel:
Task T030: "Implement add_task MCP tool in backend/src/mcp_server/tools/add_task.py"
Task T035: "Implement intent detection for Add intent in backend/src/agent/intents.py"
Task T048: "Install OpenAI ChatKit package in frontend/package.json"

# Launch typing indicator and error display in parallel:
Task T054: "Add typing indicator during agent processing in frontend/src/pages/SmartTodoApp.tsx"
Task T055: "Add error message display in ChatKit in frontend/src/pages/SmartTodoApp.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - All P1)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T029) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T030-T055) - Natural language todo creation
4. Complete Phase 4: User Story 2 (T056-T079) - Full CRUD operations
5. Complete Phase 5: User Story 3 (T080-T096) - Conversation persistence
6. **STOP and VALIDATE**: Test all P1 user stories independently
7. Add Phase 6: User Story 4 (T097-T115) - Authentication (required for production)
8. Add Phase 7: User Story 5 (T116-T131) - Stateless validation
9. Complete Phase 8: Polish (T132-T156)
10. Deploy to production

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP demo (basic todo creation)
3. Add User Story 2 → Test independently → Enhanced demo (full CRUD)
4. Add User Story 3 → Test independently → Production-ready demo (persistence)
5. Add User Story 4 → Test independently → Secure system
6. Add User Story 5 → Test independently → Scalable system
7. Polish → Production deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T029)
2. Once Foundational is done:
   - Developer A: User Story 1 (T030-T055)
   - Developer B: User Story 2 (T056-T079)
   - Developer C: User Story 3 (T080-T096)
3. Integration point: Merge and test stories together
4. Developer D: User Story 4 (T097-T115)
5. Developer E: User Story 5 (T116-T131)
6. All developers: Polish tasks in parallel (T132-T156)

---

## Notes

- **Total Tasks**: 156 tasks across 8 phases
- **MVP Scope**: Phases 1-5 (T001-T096) = 96 tasks for P1 user stories
- **Production Ready**: Add Phases 6-7 (T097-T131) for authentication and stateless validation
- **Tests**: Test tasks are omitted as tests were not explicitly requested in specification
- **[P] tasks**: 61 tasks marked as parallelizable (different files, no dependencies)
- **[Story] labels**: US1 (26 tasks), US2 (24 tasks), US3 (17 tasks), US4 (19 tasks), US5 (16 tasks)
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid cross-story dependencies that break independence

---

## Success Metrics Reference (from spec.md)

All tasks contribute to these success criteria:

- **SC-001**: Users create todos using natural language with 90%+ success rate → User Story 1
- **SC-002**: 100% of CRUD operations via MCP tools → User Story 2
- **SC-003**: 100% conversation persistence across server restarts → User Story 3
- **SC-004**: Conversation history loads in <1 second (p95) → User Story 3
- **SC-005**: AI agent responds in <3 seconds (p95) → User Stories 1, 2
- **SC-006**: 100% conversation resume after browser reload → User Story 3
- **SC-007**: Stateless architecture validated (multiple instances) → User Story 5
- **SC-008**: 100% user isolation (Better Auth) → User Story 4
- **SC-009**: 0% technical jargon in error messages → All stories
- **SC-010**: ChatKit displays typing indicators and status → User Story 1
- **SC-011**: 50 concurrent users supported without degradation → User Story 5
- **SC-012**: Neon cold start <2 seconds → Foundational Phase
