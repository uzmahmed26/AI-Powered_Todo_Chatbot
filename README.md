# Phase III Smart Todo ChatKit App

An AI-powered conversational todo management application built with OpenAI ChatKit UI, OpenAI Agents SDK, Official MCP SDK, and Neon Serverless PostgreSQL.

## 🎯 Project Overview

This project implements a stateless, AI-driven chat interface for managing todo tasks using natural language. Users interact with an AI agent through a ChatKit UI to create, read, update, and delete tasks without needing specific command syntax.

### Key Features

- 🤖 **Natural Language Processing**: Create and manage tasks using conversational language
- 💬 **ChatKit UI**: Modern chat interface powered by OpenAI ChatKit (React/TypeScript)
- 🔧 **MCP Tools**: 5 stateless tools for task management (add, list, complete, delete, update)
- 🧠 **AI Agent**: OpenAI Agents SDK with GPT-4 for intent recognition and tool orchestration
- 🗄️ **Persistent Storage**: Neon Serverless PostgreSQL with SQLModel ORM
- 🔐 **User Authentication**: Better Auth for secure, isolated user data
- ⚡ **Stateless Architecture**: Fully stateless FastAPI backend for horizontal scaling
- 💾 **Conversation History**: Persistent chat history that resumes after server restarts

## 🏗️ Architecture

```
User → ChatKit UI → FastAPI Endpoint → OpenAI Agent → MCP Tools → Database
  ↑                                         ↓              ↓
  └─────────── Conversation History ────────┴──── Tasks ───┘
```

### Technology Stack

#### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: OpenAI ChatKit
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Auth**: Better Auth React SDK

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLModel (Pydantic + SQLAlchemy)
- **Database**: Neon Serverless PostgreSQL
- **AI**: OpenAI Agents SDK (GPT-4)
- **MCP**: Official MCP SDK (Python)
- **Migrations**: Alembic
- **Server**: Uvicorn (ASGI)

## 📁 Project Structure

```
phase3/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── database/          # Database engine and session management
│   │   ├── models/            # SQLModel models (Task, Conversation, Message)
│   │   ├── mcp_server/        # MCP server and tool implementations
│   │   │   └── tools/         # Individual MCP tools
│   │   ├── agent/             # OpenAI Agent integration
│   │   ├── api/               # FastAPI routes and middleware
│   │   │   ├── routes/        # API endpoints
│   │   │   ├── middleware/    # CORS, auth, error handling
│   │   │   └── services/      # Business logic services
│   │   └── auth/              # Better Auth integration
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Unit and integration tests
│   ├── pyproject.toml         # Python dependencies
│   ├── requirements.txt       # Pip requirements
│   └── .env.example           # Environment variables template
│
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── pages/             # Page components (SmartTodoApp)
│   │   ├── components/        # Reusable components
│   │   └── services/          # API client and services
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── .env.example           # Frontend environment template
│
├── specs/                      # Specifications and planning
│   └── 002-smart-todo-chatkit/
│       ├── spec.md            # Feature specification (5 user stories)
│       ├── plan.md            # 8-phase implementation plan
│       └── tasks.md           # 156 atomic implementation tasks
│
├── docs/                       # Documentation
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Neon Serverless PostgreSQL** account
- **OpenAI API key** (for GPT-4 access)
- **Better Auth** setup (for authentication)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials:
   # - DATABASE_URL (Neon PostgreSQL connection string)
   # - OPENAI_API_KEY (OpenAI API key)
   # - BETTER_AUTH_SECRET (Better Auth secret key)
   ```

5. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**:
   ```bash
   uvicorn src.api.app:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # - VITE_API_URL=http://localhost:8000
   # - VITE_BETTER_AUTH_URL (your Better Auth domain)
   ```

4. **Start the development server**:
   ```bash
   npm run dev
   ```

5. **Open browser**: Navigate to `http://localhost:5173`

## 📋 Implementation Status

### ✅ Phase 1: Setup (COMPLETE)
- [X] Project structure created
- [X] Backend initialized (FastAPI, SQLModel, OpenAI, MCP)
- [X] Frontend initialized (React, TypeScript, ChatKit)
- [X] Linting configured (Black, Ruff, ESLint, Prettier)
- [X] Environment templates created
- [X] Git repository configured

### 🚧 Phase 2: Foundational (IN PROGRESS)
- [X] Database engine and session management
- [X] SQLModel models (Task, Conversation, Message)
- [X] Database migration setup (Alembic)
- [X] MCP tool schemas defined
- [ ] MCP server implementation
- [ ] OpenAI Agent initialization
- [ ] FastAPI application structure
- [ ] API middleware (CORS, auth, logging, errors)

### ⏳ Phase 3-8: User Stories & Polish (PENDING)
- [ ] User Story 1: Natural Language Todo Creation (P1, MVP)
- [ ] User Story 2: Todo CRUD via Chat (P1)
- [ ] User Story 3: Conversation Persistence & Resume (P1)
- [ ] User Story 4: Authentication with Better Auth (P2)
- [ ] User Story 5: Stateless FastAPI Endpoint (P2)
- [ ] Polish & Cross-Cutting Concerns

**Progress**: 17/156 tasks completed (10.9%)

## 🎯 User Stories

### Priority 1 (MVP)

1. **Natural Language Todo Creation** - Users create todos through ChatKit using natural language
2. **Todo CRUD via Chat** - Users view, update, complete, delete tasks through conversation
3. **Conversation Persistence** - Conversations persist and resume after server restarts

### Priority 2 (Production)

4. **Authentication** - Users authenticate with Better Auth, todos are user-isolated
5. **Stateless Architecture** - FastAPI endpoint is fully stateless for horizontal scaling

## 🛠️ Development Commands

### Backend

```bash
# Run tests
pytest

# Format code
black src tests

# Lint code
ruff check src tests

# Type check
mypy src

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend

```bash
# Run tests
npm test

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type check
npm run type-check

# Build for production
npm run build
```

## 📊 Success Criteria

- ✅ Users create todos using natural language with 90%+ success rate
- ✅ 100% of CRUD operations via MCP tools
- ✅ 100% conversation persistence across server restarts
- ✅ Conversation history loads in <1 second (p95)
- ✅ AI agent responds in <3 seconds (p95)
- ✅ 100% conversation resume after browser reload
- ✅ Stateless architecture validated (multiple instances)
- ✅ 100% user isolation (Better Auth)
- ✅ 0% technical jargon in error messages
- ✅ 50 concurrent users supported without degradation

## 🔒 Security

- **User Isolation**: All data scoped to user_id from Better Auth
- **SQL Injection Prevention**: SQLModel ORM with parameterized queries
- **Input Validation**: Pydantic models at API boundary
- **HTTPS**: Required in production
- **Authentication**: Better Auth session management
- **CORS**: Configured for allowed origins only

## 📖 API Documentation

Once the backend is running, access interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

This project follows Spec-Driven Development (SDD) methodology:

1. All features start with specifications (specs/)
2. Specifications are converted to implementation plans (plan.md)
3. Plans are broken into atomic tasks (tasks.md)
4. Tasks are implemented following strict checklist format
5. Prompt History Records (PHRs) document all AI interactions

## 📝 License

Proprietary - Phase III AI-Powered Todo Chatbot Project

## 🆘 Support

For issues or questions:
- Check specs/ for feature requirements
- Review tasks.md for implementation details
- Consult plan.md for architecture decisions
- Review Prompt History Records in history/prompts/

---

**Status**: 🚧 Under Active Development
**Current Phase**: Phase 2 - Foundational Prerequisites
**Next Milestone**: Complete Phase 2 foundation, begin User Story 1 (MVP)
