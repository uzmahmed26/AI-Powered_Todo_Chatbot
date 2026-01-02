---
title: Smart Todo ChatKit Backend API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: AI-powered todo management backend with FastAPI and GPT-4
---

# 🤖 Smart Todo ChatKit Backend API

AI-powered todo management backend built with FastAPI and GPT-4. This backend provides RESTful APIs for user authentication, task management, and natural language chat interactions.

## 🌟 Features

- **🔐 User Authentication**: JWT-based authentication with secure password hashing
- **📝 Task Management**: Full CRUD operations for todos with smart categorization
- **🔄 Recurring Tasks**: Support for daily, weekly, and monthly recurring tasks
- **💬 AI Chat Interface**: Natural language task management using GPT-4
- **🌍 Multi-Language Support**: English, Urdu, Arabic, Chinese, and Turkish
- **🎤 Voice Input**: Speech-to-text task creation
- **🔍 Smart Search**: Advanced filtering and search capabilities
- **⚡ Agent Skills**: Reusable AI-powered operations

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database
- OpenAI API key

### Environment Variables

Set the following environment variables in Hugging Face Space Settings:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# OpenAI
OPENAI_API_KEY=sk-...

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Optional: CORS (if frontend is on different domain)
CORS_ORIGINS=https://your-frontend-url.com
```

## 📚 API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-space-url.hf.space/docs`
- **ReDoc**: `https://your-space-url.hf.space/redoc`

## 🔌 Main Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PUT /api/tasks/{id}/complete` - Mark task as complete

### Chat
- `POST /api/chat/message` - Send message to AI assistant
- `GET /api/chat/conversations` - List user conversations
- `GET /api/chat/conversations/{id}` - Get conversation by ID

### Skills
- `GET /api/skills` - List available agent skills
- `POST /api/skills/execute` - Execute a specific skill

## 🏗️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLModel
- **AI**: OpenAI GPT-4
- **Authentication**: JWT (python-jose)
- **Password Hashing**: Passlib with bcrypt
- **Migrations**: Alembic

## 📦 Deployment to Hugging Face

1. Create a new Space on Hugging Face
2. Select **Docker** as SDK
3. Upload all backend files
4. Set environment variables in Space Settings
5. The Space will automatically build and deploy

## 🔒 Security Notes

- All passwords are hashed using bcrypt
- JWT tokens expire after 15 minutes (access) and 7 days (refresh)
- CORS is configured for security
- SQL injection protection via SQLModel ORM
- Input validation with Pydantic

## 📝 License

MIT License - see LICENSE file for details

## 👥 Contributors

Built with ❤️ using Claude Code and GPT-4
