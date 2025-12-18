---
id: 001
title: Smart Todo ChatKit Specification
stage: spec
date: 2025-12-17
surface: agent
model: claude-sonnet-4-5
feature: 002-smart-todo-chatkit
branch: 002-smart-todo-chatkit
user: user
command: /sp.specify
labels: ["specification", "smart-todo", "chatkit", "openai-agents", "mcp", "sqlmodel", "neon", "better-auth"]
links:
  spec: ../../specs/002-smart-todo-chatkit/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-smart-todo-chatkit/spec.md
  - specs/002-smart-todo-chatkit/checklists/requirements.md
tests:
  - None (specification phase)
---

## Prompt

Project: Phase III — AI-Powered Todo Chatbot

Objective:
Build an AI-powered chatbot interface for managing todos using natural language,
based on MCP (Model Context Protocol) server architecture.

Development Approach:
Agentic Dev Stack using Spec-Kit Plus and Claude Code.
No manual coding allowed.

Core Requirements:
- Conversational UI using OpenAI ChatKit
- Stateless FastAPI chat endpoint
- OpenAI Agents SDK for AI logic
- Official MCP SDK for tool-based task operations
- Conversation persistence in database
- Resume conversations after server restart

Technology Stack:
Frontend: OpenAI ChatKit
Backend: Python FastAPI
AI Framework: OpenAI Agents SDK
MCP Server: Official MCP SDK
ORM: SQLModel
Database: Neon Serverless PostgreSQL
Authentication: Better Auth

Scope:
Only Smart Todo App page
No global chatbot

## Response snapshot

Created comprehensive feature specification for **Smart Todo ChatKit App** (branch: 002-smart-todo-chatkit) with mandated technology stack:

**Technology Stack** (User-Mandated Constraints):
- Frontend: OpenAI ChatKit (React/TypeScript components)
- Backend: Python FastAPI (stateless chat endpoint)
- AI: OpenAI Agents SDK (NLU, intent extraction, tool orchestration)
- MCP: Official MCP SDK (tool-based todo operations)
- ORM: SQLModel (type-safe, Pydantic-compatible)
- Database: Neon Serverless PostgreSQL (cloud-hosted, auto-scaling)
- Auth: Better Auth (production-ready authentication)

**User Stories** (5 total, prioritized P1-P2):
- **P1**: Natural Language Todo Creation (validates AI + MCP integration)
- **P1**: Todo CRUD Operations via Chat (completes MVP functionality)
- **P1**: Conversation Persistence & Resume (stateless architecture validation)
- **P2**: Authentication with Better Auth (security and user isolation)
- **P2**: Stateless FastAPI Endpoint (architectural requirement)

**Requirements**:
- 20 functional requirements (FR-001 through FR-020)
- 4 key entities: User (Better Auth), Todo, Conversation, Message (nested)
- 12 success criteria with measurable metrics
- 10 edge cases identified (API failures, database issues, concurrency)
- Technology stack documented as user-mandated constraints

**Key Architecture Decisions**:
1. **Stateless Backend**: Zero in-memory state, all conversation data in Neon database
2. **MCP Tools**: 6 tools (create_todo, list_todos, get_todo, update_todo, delete_todo, complete_todo)
3. **OpenAI Agent Orchestration**: Agent handles NLU, intent extraction, tool calling
4. **Conversation Persistence**: JSONB array in Neon for flexible message schema
5. **Scope Constraint**: Only Smart Todo App page (not global chatbot)

**Quality Validation**:
- All checklist items pass ✅
- Zero [NEEDS CLARIFICATION] markers
- Technology stack is user-mandated (documented as constraints, not implementation choices)
- Success criteria are user-focused and measurable

**Workflow Example**:
User: "Remind me to buy milk tomorrow"
→ ChatKit → FastAPI (auth via Better Auth)
→ Load conversation from Neon
→ OpenAI Agent extracts intent + entities
→ Agent calls MCP tool: create_todo(title="buy milk", due_date="2025-12-18")
→ SQLModel inserts into Neon
→ Agent generates response: "✓ Added 'buy milk' to your tasks for tomorrow"
→ Save conversation to Neon
→ Return to ChatKit

## Outcome

- ✅ Impact: Complete feature specification created with user-mandated technology stack (OpenAI ChatKit, OpenAI Agents SDK, Official MCP SDK, SQLModel, Neon, Better Auth)
- 🧪 Tests: No tests at specification phase; test requirements defined in acceptance scenarios
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: /sp.plan to create implementation plan with MCP SDK integration details, SQLModel schema, OpenAI Agent configuration
- 🧠 Reflection: Specification successfully captures stateless architecture requirement and scope constraint (Smart Todo App page only). Technology stack is user-mandated, documented as constraints rather than implementation decisions. Key integration points identified: OpenAI Agents SDK + MCP SDK, Better Auth + FastAPI, SQLModel + Neon.

## Evaluation notes (flywheel)

- Failure modes observed: None; specification completed successfully with all validation checks passing
- Graders run and results (PASS/FAIL): Requirements checklist - ALL PASS (content quality, requirement completeness, feature readiness)
- Prompt variant (if applicable): Standard /sp.specify workflow with user-mandated technology stack
- Next experiment (smallest change to try): Proceed to /sp.plan to verify compatibility of mandated technologies (OpenAI Agents SDK + Official MCP SDK integration, SQLModel + Neon setup, Better Auth + FastAPI integration)
