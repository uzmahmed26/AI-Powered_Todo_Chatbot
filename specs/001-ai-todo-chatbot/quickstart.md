# Quickstart Guide: AI-Powered Todo Chatbot
**Feature**: 001-ai-todo-chatbot
**Date**: 2025-12-17

## Prerequisites
- Docker & Docker Compose installed
- Git installed
- Anthropic API key (get from https://console.anthropic.com/)
- 8GB RAM minimum, 16GB recommended
- Ports available: 3000 (frontend), 8000 (backend), 8001 (MCP server), 5432 (PostgreSQL), 6379 (Redis)

## Quick Start (5 minutes)

### 1. Clone & Setup
```bash
# Clone repository
git clone <repo-url>
cd ai-todo-chatbot

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```bash
# Required: Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...

# Database (defaults work for Docker)
DATABASE_URL=postgresql://todo_user:todo_pass@postgres:5432/todo_db

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=your-generated-secret-here

# Optional: Adjust ports if needed
FRONTEND_PORT=3000
BACKEND_PORT=8000
MCP_SERVER_PORT=8001
```

### 3. Start All Services
```bash
# Start all containers (frontend, backend, MCP server, PostgreSQL, Redis)
docker-compose up -d

# Verify all services are running
docker-compose ps

# Expected output:
# NAME           STATUS     PORTS
# frontend       Up         0.0.0.0:3000->3000/tcp
# backend        Up         0.0.0.0:8000->8000/tcp
# mcp-server     Up         0.0.0.0:8001->8001/tcp
# postgres       Up         0.0.0.0:5432->5432/tcp
# redis          Up         0.0.0.0:6379->6379/tcp
```

### 4. Run Database Migrations
```bash
# Run Alembic migrations to create schema
docker-compose exec mcp-server alembic upgrade head

# Verify tables created
docker-compose exec postgres psql -U todo_user -d todo_db -c "\dt"

# Expected output:
#  Schema |      Name       | Type  | Owner
# --------+-----------------+-------+-----------
#  public | users           | table | todo_user
#  public | todos           | table | todo_user
#  public | conversations   | table | todo_user
#  public | user_preferences| table | todo_user
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs (Swagger UI)
- **MCP Server API Docs**: http://localhost:8001/docs (Swagger UI)

### 6. Create Account & Test
1. Navigate to http://localhost:3000
2. Click "Sign Up" and create an account
3. Test natural language todo creation:
   - "Remind me to buy milk tomorrow"
   - "Add task: finish report by Friday"
   - "Show my tasks"

## Development Workflow

### Local Development (Hot Reload)

**Backend (Python)**:
```bash
# Enter backend container
docker-compose exec backend bash

# Run with hot reload (uvicorn --reload)
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (React)**:
```bash
# Frontend already has hot reload enabled by default
# Edit files in frontend/src/ and see changes instantly

# Or run locally (outside Docker):
cd frontend
npm install
npm start
```

**MCP Server**:
```bash
# Enter MCP server container
docker-compose exec mcp-server bash

# Run with hot reload
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Running Tests

**All Tests**:
```bash
# Run all tests across all services
docker-compose exec backend pytest
docker-compose exec mcp-server pytest
docker-compose exec frontend npm test
```

**Specific Test Suites**:
```bash
# Backend unit tests only
docker-compose exec backend pytest tests/unit/

# MCP server contract tests
docker-compose exec mcp-server pytest tests/contract/

# Frontend component tests
docker-compose exec frontend npm test -- ChatInterface.test.tsx
```

**Integration Tests** (End-to-end):
```bash
# Requires all services running
docker-compose exec backend pytest tests/integration/

# Or run E2E tests from host
pytest tests/e2e/
```

### Database Management

**View Logs**:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f mcp-server
```

**Reset Database**:
```bash
# WARNING: Deletes all data
docker-compose down -v  # Remove volumes
docker-compose up -d
docker-compose exec mcp-server alembic upgrade head
```

**Database Shell**:
```bash
# PostgreSQL interactive shell
docker-compose exec postgres psql -U todo_user -d todo_db

# Useful queries:
# SELECT * FROM users;
# SELECT * FROM todos WHERE user_id = '<uuid>';
# SELECT messages FROM conversations WHERE user_id = '<uuid>';
```

**Create Migration** (After schema changes):
```bash
# Enter MCP server container
docker-compose exec mcp-server bash

# Auto-generate migration
alembic revision --autogenerate -m "description of change"

# Review generated file in migrations/
# Edit if needed, then apply:
alembic upgrade head
```

## Architecture Overview

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
┌──────▼──────────┐
│ Frontend (React)│ :3000
└──────┬──────────┘
       │ REST API (JWT)
┌──────▼─────────────┐
│ Backend (FastAPI)  │ :8000
│ - AI Service       │
│ - Intent Parser    │
│ - MCP Client       │
└──────┬─────┬───────┘
       │     │
       │     └────────────┐
┌──────▼────────┐  ┌──────▼──────────┐
│ Claude API    │  │ MCP Server      │ :8001
│ (Anthropic)   │  │ - Todo CRUD     │
└───────────────┘  │ - SQLAlchemy    │
                   └─────────┬────────┘
                             │
                   ┌─────────▼─────────┐
                   │ PostgreSQL        │ :5432
                   │ - users           │
                   │ - todos           │
                   │ - conversations   │
                   └───────────────────┘
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 3000 (example)
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process or change port in .env
FRONTEND_PORT=3001
```

### Database Connection Errors
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection from MCP server
docker-compose exec mcp-server bash
python -c "from src.db.connection import engine; print(engine.connect())"
```

### Anthropic API Errors
```bash
# Verify API key is set
docker-compose exec backend env | grep ANTHROPIC

# Test API key manually
docker-compose exec backend python
>>> from anthropic import Anthropic
>>> client = Anthropic(api_key="sk-ant-...")
>>> client.messages.create(model="claude-3-5-sonnet-20241022", messages=[{"role":"user","content":"hi"}], max_tokens=10)
```

### Frontend Not Loading
```bash
# Check frontend build logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Access directly (skip nginx)
curl http://localhost:3000
```

### Tests Failing
```bash
# Ensure test database is clean
docker-compose exec mcp-server alembic downgrade base
docker-compose exec mcp-server alembic upgrade head

# Run with verbose output
docker-compose exec backend pytest -v -s

# Run specific test
docker-compose exec backend pytest tests/unit/test_date_parser.py -k "test_tomorrow"
```

## Production Deployment

See [deployment.md](../../docs/deployment.md) for production deployment guide including:
- Kubernetes configuration (bonus feature P3)
- Environment variable management
- SSL/TLS setup
- Monitoring & alerting
- Backup & recovery
- Scaling strategies

## Performance Benchmarks

Expected performance metrics (after warming up):

| Operation | Latency (p50) | Latency (p95) |
|-----------|---------------|---------------|
| Create todo (NL) | 800ms | 1500ms |
| List todos | 50ms | 100ms |
| Update todo | 30ms | 60ms |
| Mark completed | 30ms | 60ms |
| Chat response | 600ms | 1200ms |

**Load Testing**:
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Access Locust UI: http://localhost:8089
# Configure: 100 users, 10 users/sec spawn rate
```

## Next Steps

1. ✅ **Application Running** - All services up
2. ✅ **Account Created** - User registered and logged in
3. ✅ **Basic Testing** - Natural language todo creation works
4. ⏭️ **Explore Features** - Try CRUD operations, context-aware conversations
5. ⏭️ **Run Tests** - Verify all test suites pass
6. ⏭️ **Review Code** - Explore backend/, mcp-server/, frontend/ structure
7. ⏭️ **Contribute** - See CONTRIBUTING.md for development guidelines

## Getting Help

- **Issues**: https://github.com/<org>/<repo>/issues
- **Discussions**: https://github.com/<org>/<repo>/discussions
- **Documentation**: `/docs` directory
- **API Docs**: http://localhost:8000/docs (backend), http://localhost:8001/docs (MCP server)

**Common Questions**:
- Q: How do I add a new MCP tool?
  A: Add endpoint to `mcp-server/src/api/`, update OpenAPI spec, implement in `todo_service.py`

- Q: How do I change the AI model?
  A: Update `ANTHROPIC_MODEL` in `.env` (options: claude-3-5-sonnet-20241022, claude-3-opus-20240229)

- Q: How do I enable bonus features?
  A: See plan.md Bonus Features section for implementation guidance

## Summary

You should now have:
✅ All services running (frontend, backend, MCP server, PostgreSQL, Redis)
✅ Database schema created via migrations
✅ Application accessible at http://localhost:3000
✅ API documentation at http://localhost:8000/docs
✅ Test suites passing

**Start using the AI-powered todo chatbot!** 🎉
