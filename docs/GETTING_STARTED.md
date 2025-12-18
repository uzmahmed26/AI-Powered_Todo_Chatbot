# Getting Started - Phase III Smart Todo ChatKit App

## 🚀 Quick Start Guide

This guide will help you set up and run the Phase III Smart Todo ChatKit App MVP (User Story 1 - Natural Language Todo Creation).

## Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Neon Serverless PostgreSQL** account (https://neon.tech)
- **OpenAI API key** (https://platform.openai.com)

## Setup Instructions

### 1. Clone and Navigate

```bash
cd phase3
```

### 2. Backend Setup

#### Install Dependencies

```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install packages
pip install -r requirements.txt
```

#### Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your credentials:
# - DATABASE_URL: Your Neon PostgreSQL connection string
# - OPENAI_API_KEY: Your OpenAI API key
# - BETTER_AUTH_SECRET: Any secure random string (32+ characters)
```

**Example .env**:
```env
DATABASE_URL=postgresql+asyncpg://user:password@ep-xyz.us-east-1.aws.neon.tech/smarttodo?sslmode=require
OPENAI_API_KEY=sk-proj-...
BETTER_AUTH_SECRET=your-secure-secret-key-min-32-characters
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
MAX_CONTEXT_MESSAGES=20
```

#### Run Database Migrations

```bash
# Apply migrations to create database tables
alembic upgrade head
```

#### Start Backend Server

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using uvicorn directly
uvicorn src.api.app:app --reload --port 8000
```

The backend API will be available at: **http://localhost:8000**

- API Documentation (Swagger): http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Frontend Setup

#### Install Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults should work):
VITE_API_URL=http://localhost:8000
```

#### Start Frontend Server

```bash
npm run dev
```

The frontend will be available at: **http://localhost:5173**

## Usage

### Testing the MVP (User Story 1)

1. **Open your browser** and navigate to http://localhost:5173

2. **Try these natural language commands**:
   - "Add buy milk to my tasks"
   - "Remind me to call mom tomorrow"
   - "I need to finish the report by Friday"
   - "Create a task for groceries"

3. **Verify the backend**:
   - Check the terminal running the backend to see logs
   - Visit http://localhost:8000/docs to test the API directly

### API Testing with Swagger

1. Navigate to http://localhost:8000/docs
2. Expand `POST /api/{user_id}/chat`
3. Click "Try it out"
4. Enter:
   - `user_id`: `demo-user`
   - Request body:
     ```json
     {
       "message": "Add buy milk",
       "conversation_id": null
     }
     ```
5. Click "Execute"
6. See the response with created task

## Architecture Overview

### Current Implementation (Phase 3 - User Story 1)

```
Frontend (React + TypeScript)
  ↓ HTTP POST /api/{user_id}/chat
Backend (FastAPI)
  ↓ Load conversation from DB
Database (Neon PostgreSQL)
  ↓ Process with AI Agent
OpenAI Agent (GPT-4)
  ↓ Call MCP tool
add_task MCP Tool
  ↓ Store task in DB
Database (Neon PostgreSQL)
  ↑ Return response
Frontend (Display result)
```

### What's Implemented

✅ **Phase 1**: Setup (8 tasks)
- Project structure
- Backend (FastAPI, SQLModel, OpenAI SDK)
- Frontend (React, TypeScript, Vite)
- Configuration and linting

✅ **Phase 2**: Foundational (21 tasks)
- Database models (Task, Conversation, Message)
- MCP server framework
- AI agent (TodoAgent with OpenAI)
- FastAPI app with middleware

✅ **Phase 3 User Story 1**: Natural Language Todo Creation (26 tasks)
- add_task MCP tool
- Intent recognition and parameter extraction
- Stateless chat endpoint
- ChatKit UI integration
- Conversation persistence

**Total**: 55/156 tasks (35.3%)

## Troubleshooting

### Backend won't start

**Error**: `DATABASE_URL environment variable is required`
- **Solution**: Make sure you've created `.env` file and added your Neon database URL

**Error**: `OPENAI_API_KEY environment variable is required`
- **Solution**: Add your OpenAI API key to `.env` file

**Error**: Database connection failed
- **Solution**: Verify your Neon database is active and the connection string is correct

### Frontend won't connect to backend

**Error**: API requests failing
- **Solution**: Make sure backend is running on port 8000
- **Solution**: Check CORS settings in backend/.env (ALLOWED_ORIGINS)

### Database migrations fail

**Error**: `alembic upgrade head` fails
- **Solution**: Make sure DATABASE_URL is set correctly
- **Solution**: Check Neon database is accessible

## Development Commands

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
```

### Frontend

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint

# Format
npm run format

# Type check
npm run type-check
```

## Next Steps

After User Story 1 is working:

1. **User Story 2**: Implement list, complete, delete, update MCP tools
2. **User Story 3**: Add conversation persistence and resume
3. **User Story 4**: Integrate Better Auth for authentication
4. **User Story 5**: Validate stateless architecture

## Support

- **Documentation**: See README.md for full details
- **API Docs**: http://localhost:8000/docs
- **Specifications**: See specs/002-smart-todo-chatkit/spec.md
- **Tasks**: See specs/002-smart-todo-chatkit/tasks.md

## Demo User ID

For MVP testing (before Better Auth integration), use:
- **User ID**: `demo-user`

This is hardcoded in the frontend (SmartTodoApp.tsx:22) and will be replaced with actual authentication in Phase 6 (User Story 4).
