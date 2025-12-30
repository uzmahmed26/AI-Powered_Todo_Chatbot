# Implementation Guide: Todo System Upgrade

**Feature**: 008-todo-upgrade
**Estimated Time**: 6-8 hours
**Difficulty**: Intermediate

This guide provides step-by-step instructions for implementing the todo system upgrade with priority, categories, due dates, search, filtering, and sorting.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Phase 1: Database Schema](#2-phase-1-database-schema)
3. [Phase 2: Update Task Model](#3-phase-2-update-task-model)
4. [Phase 3: Update MCP Schemas](#4-phase-3-update-mcp-schemas)
5. [Phase 4: Update MCP Tools](#5-phase-4-update-mcp-tools)
6. [Phase 5: Update AI Agent](#6-phase-5-update-ai-agent)
7. [Phase 6: Frontend Integration](#7-phase-6-frontend-integration-optional)
8. [Phase 7: Testing](#8-phase-7-testing)

---

## 1. Prerequisites

- Backend server running on port 8000
- Frontend server running on port 5173
- PostgreSQL database running
- Python virtual environment activated
- Node modules installed

**Verify Setup**:
```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.api.app:app --reload --port 8000

# Frontend (in separate terminal)
cd frontend
npm run dev
```

---

## 2. Phase 1: Database Schema

### Step 1: Create Migration File

Create `backend/alembic/versions/003_add_task_enhancements.py`:

```python
"""add task enhancements: priority, category, due_date

Revision ID: 003
Revises: 002
Create Date: 2025-12-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add priority, category, and due_date columns to tasks table."""

    # Add priority column with default 'medium'
    op.add_column(
        'tasks',
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium')
    )

    # Add category column (nullable)
    op.add_column(
        'tasks',
        sa.Column('category', sa.String(length=50), nullable=True)
    )

    # Add due_date column (nullable)
    op.add_column(
        'tasks',
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True)
    )

    # Create indexes for performance
    op.create_index('idx_task_priority', 'tasks', ['priority'])
    op.create_index('idx_task_category', 'tasks', ['category'])
    op.create_index('idx_task_due_date', 'tasks', ['due_date'])

    # Create composite index for common query pattern
    op.create_index(
        'idx_task_user_status_priority',
        'tasks',
        ['user_id', 'completed', 'priority']
    )


def downgrade() -> None:
    """Remove priority, category, and due_date columns."""

    # Drop indexes
    op.drop_index('idx_task_user_status_priority', table_name='tasks')
    op.drop_index('idx_task_due_date', table_name='tasks')
    op.drop_index('idx_task_category', table_name='tasks')
    op.drop_index('idx_task_priority', table_name='tasks')

    # Drop columns
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'category')
    op.drop_column('tasks', 'priority')
```

### Step 2: Run Migration

```bash
cd backend
alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add task enhancements
```

### Step 3: Verify Database

```bash
# Connect to PostgreSQL
psql -U postgres -d smart_todo_db

# Check schema
\d tasks

# You should see:
# - priority column (varchar, default 'medium')
# - category column (varchar, nullable)
# - due_date column (timestamp with time zone, nullable)

# Check indexes
\di

# You should see new indexes:
# - idx_task_priority
# - idx_task_category
# - idx_task_due_date
# - idx_task_user_status_priority
```

---

## 3. Phase 2: Update Task Model

### Step 1: Update `backend/src/models/task.py`

Add new fields and enums:

```python
"""
Task SQLModel for user todo items.

Represents a task/todo item in the Smart Todo App with user isolation.
All tasks are scoped to user_id for multi-tenant data isolation.
"""

from datetime import datetime
from typing import Optional, Literal
from sqlmodel import Field, SQLModel, Column, DateTime, Index
from sqlalchemy.sql import func
from enum import Enum


# Priority and Category Enums
class TaskPriority(str, Enum):
    """Task priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskCategory(str, Enum):
    """Task categories."""
    WORK = "work"
    HOME = "home"
    STUDY = "study"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    FITNESS = "fitness"


class Task(SQLModel, table=True):
    """
    Task model for storing user todo items.

    Attributes:
        id: Auto-incrementing primary key
        user_id: User identifier from JWT auth (for isolation)
        title: Task title (1-200 chars, required)
        description: Optional task description
        completed: Task completion status (default False)
        priority: Task priority (high, medium, low)
        category: Task category (work, home, study, etc.)
        due_date: Optional due date
        created_at: Timestamp when task was created
        updated_at: Timestamp when task was last updated
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False, description="User ID from JWT Auth")
    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)",
    )
    description: Optional[str] = Field(default=None, description="Optional task description")
    completed: bool = Field(default=False, index=True, description="Task completion status")

    # NEW FIELDS
    priority: str = Field(
        default="medium",
        nullable=False,
        index=True,
        description="Task priority: high, medium, low"
    )
    category: Optional[str] = Field(
        default=None,
        index=True,
        description="Task category: work, home, study, personal, shopping, health, fitness"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True,
        sa_column=Column(DateTime(timezone=True)),
        description="Task due date (optional)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
        description="Last update timestamp",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "uuid-string",
                "title": "Buy groceries",
                "description": "Milk, bread, eggs",
                "completed": False,
                "priority": "high",
                "category": "shopping",
                "due_date": "2025-01-15T10:00:00Z"
            }
        }


# Create composite index for user-specific task queries
Index("idx_task_user_completed", Task.user_id, Task.completed)
Index("idx_task_user_status_priority", Task.user_id, Task.completed, Task.priority)
```

---

## 4. Phase 3: Update MCP Schemas

### Step 1: Update `backend/src/mcp_server/schemas.py`

Add new fields to input/output schemas:

```python
"""
MCP Tool Schemas for validation and documentation.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ===== Add Task =====

class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="User ID for task isolation")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, description="Optional task description")

    # NEW FIELDS
    priority: str = Field(default="medium", description="Task priority: high, medium, low")
    category: Optional[str] = Field(None, description="Task category")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")

    @validator("priority")
    def validate_priority(cls, v):
        if v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @validator("category")
    def validate_category(cls, v):
        if v is not None and v not in ["work", "home", "study", "personal", "shopping", "health", "fitness"]:
            raise ValueError("Category must be one of: work, home, study, personal, shopping, health, fitness")
        return v

    @validator("due_date")
    def validate_due_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("due_date must be a valid ISO datetime string")
        return v


class TaskData(BaseModel):
    """Task data structure returned by tools."""
    task_id: int
    title: str
    description: Optional[str]
    status: str
    priority: str  # NEW
    category: Optional[str]  # NEW
    due_date: Optional[str]  # NEW
    created_at: Optional[str]
    updated_at: Optional[str]


class AddTaskOutput(BaseModel):
    """Output schema for add_task tool."""
    success: bool
    data: Optional[TaskData]
    message: str


# ===== Update Task =====

class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="User ID for task isolation")
    task_id: int = Field(..., description="Task ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None

    # NEW FIELDS
    priority: Optional[str] = Field(None, description="Task priority")
    category: Optional[str] = Field(None, description="Task category")
    due_date: Optional[str] = Field(None, description="Due date in ISO format")

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None and v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @validator("category")
    def validate_category(cls, v):
        if v is not None and v not in ["work", "home", "study", "personal", "shopping", "health", "fitness"]:
            raise ValueError("Category must be one of: work, home, study, personal, shopping, health, fitness")
        return v

    @validator("due_date")
    def validate_due_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("due_date must be a valid ISO datetime string")
        return v


class UpdateTaskOutput(BaseModel):
    """Output schema for update_task tool."""
    success: bool
    data: Optional[TaskData]
    message: str


# ===== List Tasks =====

class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="User ID for task isolation")
    status: str = Field(default="all", description="Filter by status: all, pending, completed")

    # NEW FILTERS
    priority: Optional[str] = Field(None, description="Filter by priority")
    category: Optional[str] = Field(None, description="Filter by category")
    search: Optional[str] = Field(None, description="Search keyword in title/description")
    due_date_from: Optional[str] = Field(None, description="Filter tasks due from this date")
    due_date_to: Optional[str] = Field(None, description="Filter tasks due until this date")
    sort_by: str = Field(default="created_at", description="Sort field: created_at, due_date, priority, title")
    sort_order: str = Field(default="desc", description="Sort order: asc, desc")

    @validator("status")
    def validate_status(cls, v):
        if v not in ["all", "pending", "completed"]:
            raise ValueError("Status must be one of: all, pending, completed")
        return v

    @validator("priority")
    def validate_priority(cls, v):
        if v is not None and v not in ["high", "medium", "low"]:
            raise ValueError("Priority must be one of: high, medium, low")
        return v

    @validator("sort_by")
    def validate_sort_by(cls, v):
        if v not in ["created_at", "due_date", "priority", "title"]:
            raise ValueError("sort_by must be one of: created_at, due_date, priority, title")
        return v

    @validator("sort_order")
    def validate_sort_order(cls, v):
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be one of: asc, desc")
        return v


class ListTasksOutput(BaseModel):
    """Output schema for list_tasks tool."""
    success: bool
    data: Optional[dict]  # Contains 'tasks' list, 'count', 'filters', 'sort'
    message: str


# ===== Complete Task (no changes) =====

class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., description="User ID for task isolation")
    task_id: int = Field(..., description="Task ID to mark complete")


class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task tool."""
    success: bool
    data: Optional[TaskData]
    message: str


# ===== Delete Task (no changes) =====

class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="User ID for task isolation")
    task_id: int = Field(..., description="Task ID to delete")


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""
    success: bool
    data: Optional[dict]
    message: str


# ===== Error Response =====

class MCPErrorResponse(BaseModel):
    """Standard error response for MCP tools."""
    success: bool = False
    data: None = None
    message: str
    error_code: str
```

---

## 5. Phase 4: Update MCP Tools

### Step 1: Update `backend/src/mcp_server/tools/add_task.py`

```python
"""
add_task MCP Tool Implementation

Creates a new task in the database with user isolation.
Supports priority, category, and due_date.
"""

from typing import Dict, Any
from datetime import datetime
import logging
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import AddTaskInput, AddTaskOutput, TaskData, MCPErrorResponse

logger = logging.getLogger(__name__)


async def execute(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",  # NEW
    category: str = None,      # NEW
    due_date: str = None       # NEW
) -> Dict[str, Any]:
    """
    Execute add_task MCP tool.

    Creates a new task for the specified user with title, description,
    priority, category, and optional due date.

    Args:
        user_id: User ID from JWT Auth (required for user isolation)
        title: Task title (1-200 characters)
        description: Optional task description
        priority: Task priority (high, medium, low) - defaults to medium
        category: Task category (work, home, study, etc.) - optional
        due_date: Due date in ISO format - optional

    Returns:
        Dictionary with success status, task data, and message

    Example:
        result = await execute(
            user_id="uuid-123",
            title="Buy groceries",
            description="Milk, bread, eggs",
            priority="high",
            category="shopping",
            due_date="2025-01-15T10:00:00Z"
        )
    """
    try:
        # Parse due_date if provided
        parsed_due_date = None
        if due_date:
            try:
                parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                return {
                    "success": False,
                    "data": None,
                    "message": "Invalid due_date format. Use ISO format (e.g., 2025-01-15T10:00:00Z)",
                    "error_code": "VALIDATION_ERROR",
                }

        # Validate input using Pydantic schema
        input_data = AddTaskInput(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            category=category,
            due_date=due_date,
        )

        logger.info(f"Creating task for user {user_id}: '{title}' (priority={priority}, category={category})")

        # Create database session
        async with async_session_maker() as session:
            # Create new task
            new_task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                completed=False,
                priority=input_data.priority,
                category=input_data.category,
                due_date=parsed_due_date,
            )

            # Add to database
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

            logger.info(f"Task created successfully: task_id={new_task.id}")

            # Build response data
            result = {
                "success": True,
                "data": {
                    "task_id": new_task.id,
                    "title": new_task.title,
                    "description": new_task.description,
                    "status": "pending" if not new_task.completed else "completed",
                    "priority": new_task.priority,
                    "category": new_task.category,
                    "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                    "created_at": new_task.created_at.isoformat() if new_task.created_at else None,
                    "updated_at": new_task.updated_at.isoformat() if new_task.updated_at else None,
                },
                "message": "Task created successfully",
            }

            return result

    except ValueError as e:
        # Validation error
        logger.warning(f"Validation error in add_task: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error creating task: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to create task. Please try again.",
            "error_code": "SERVER_ERROR",
        }
```

### Step 2: Update `backend/src/mcp_server/tools/update_task.py`

Add similar changes to support priority, category, and due_date updates. The key changes:

```python
async def execute(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,   # NEW
    category: str = None,   # NEW
    due_date: str = None    # NEW
) -> Dict[str, Any]:
    # ... validation ...

    # Update fields if provided
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if priority is not None:
        task.priority = priority
    if category is not None:
        task.category = category
    if due_date is not None:
        task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))

    # ... save and return ...
```

### Step 3: Update `backend/src/mcp_server/tools/list_tasks.py`

This is the most complex update. Add filtering, search, and sorting:

```python
"""
list_tasks MCP Tool Implementation

Lists tasks for a user with filtering, search, and sorting.
"""

from typing import Dict, Any
from datetime import datetime
import logging
from sqlmodel import select, or_, func, case
from sqlmodel.ext.asyncio.session import AsyncSession

from ...models.task import Task
from ...database.engine import async_session_maker
from ..schemas import ListTasksInput, ListTasksOutput, TaskData, MCPErrorResponse

logger = logging.getLogger(__name__)


async def execute(
    user_id: str,
    status: str = "all",
    priority: str = None,          # NEW
    category: str = None,          # NEW
    search: str = None,            # NEW
    due_date_from: str = None,     # NEW
    due_date_to: str = None,       # NEW
    sort_by: str = "created_at",   # NEW
    sort_order: str = "desc"       # NEW
) -> Dict[str, Any]:
    """
    Execute list_tasks MCP tool with advanced filtering.

    Args:
        user_id: User ID from JWT Auth
        status: Filter by status (all, pending, completed)
        priority: Filter by priority (high, medium, low)
        category: Filter by category
        search: Search keyword in title/description
        due_date_from: Filter tasks due from this date (ISO format)
        due_date_to: Filter tasks due until this date (ISO format)
        sort_by: Sort field (created_at, due_date, priority, title)
        sort_order: Sort order (asc, desc)

    Returns:
        Dictionary with success status, task list, and metadata
    """
    try:
        # Validate input
        input_data = ListTasksInput(
            user_id=user_id,
            status=status,
            priority=priority,
            category=category,
            search=search,
            due_date_from=due_date_from,
            due_date_to=due_date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        logger.info(f"Listing tasks for user {user_id} (status={status}, priority={priority}, category={category})")

        # Create database session
        async with async_session_maker() as session:
            # Build query with user isolation
            query = select(Task).where(Task.user_id == input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                query = query.where(Task.completed == False)
            elif input_data.status == "completed":
                query = query.where(Task.completed == True)

            # Apply priority filter
            if input_data.priority:
                query = query.where(Task.priority == input_data.priority)

            # Apply category filter
            if input_data.category:
                query = query.where(Task.category == input_data.category)

            # Apply search (case-insensitive, partial match)
            if input_data.search:
                search_pattern = f"%{input_data.search}%"
                query = query.where(
                    or_(
                        Task.title.ilike(search_pattern),
                        Task.description.ilike(search_pattern)
                    )
                )

            # Apply due date filters
            if input_data.due_date_from:
                try:
                    date_from = datetime.fromisoformat(input_data.due_date_from.replace('Z', '+00:00'))
                    query = query.where(Task.due_date >= date_from)
                except ValueError:
                    pass

            if input_data.due_date_to:
                try:
                    date_to = datetime.fromisoformat(input_data.due_date_to.replace('Z', '+00:00'))
                    query = query.where(Task.due_date <= date_to)
                except ValueError:
                    pass

            # Apply sorting
            if input_data.sort_by == "due_date":
                # Sort with NULL values last
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.due_date.asc().nullslast())
                else:
                    query = query.order_by(Task.due_date.desc().nullslast())
            elif input_data.sort_by == "priority":
                # Custom priority order: high > medium > low
                priority_order = case(
                    (Task.priority == "high", 1),
                    (Task.priority == "medium", 2),
                    (Task.priority == "low", 3),
                    else_=4
                )
                if input_data.sort_order == "asc":
                    query = query.order_by(priority_order.asc())
                else:
                    query = query.order_by(priority_order.desc())
            elif input_data.sort_by == "title":
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.title.asc())
                else:
                    query = query.order_by(Task.title.desc())
            else:  # created_at (default)
                if input_data.sort_order == "asc":
                    query = query.order_by(Task.created_at.asc())
                else:
                    query = query.order_by(Task.created_at.desc())

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            logger.info(f"Found {len(tasks)} tasks for user {user_id}")

            # Build response data
            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": "pending" if not task.completed else "completed",
                    "priority": task.priority,
                    "category": task.category,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                })

            # Friendly message
            if len(tasks) == 0:
                message = "You don't have any tasks matching these filters."
            elif len(tasks) == 1:
                message = "Found 1 task"
            else:
                message = f"Found {len(tasks)} tasks"

            return {
                "success": True,
                "data": {
                    "tasks": task_list,
                    "count": len(tasks),
                    "filters": {
                        "status": input_data.status,
                        "priority": input_data.priority,
                        "category": input_data.category,
                        "search": input_data.search,
                    },
                    "sort": {
                        "by": input_data.sort_by,
                        "order": input_data.sort_order,
                    }
                },
                "message": message,
            }

    except ValueError as e:
        logger.warning(f"Validation error in list_tasks: {e}")
        return {
            "success": False,
            "data": None,
            "message": f"Invalid input: {str(e)}",
            "error_code": "VALIDATION_ERROR",
        }

    except Exception as e:
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        return {
            "success": False,
            "data": None,
            "message": "Failed to retrieve tasks. Please try again.",
            "error_code": "SERVER_ERROR",
        }
```

### Step 4: Update MCP Server Tool Definitions

Update `backend/src/mcp_server/server.py` to register new tool parameters:

```python
# In the tools list, update add_task definition:
{
    "name": "add_task",
    "description": "Add a new task to the user's todo list with priority, category, and due date",
    "inputSchema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string", "description": "User ID"},
            "title": {"type": "string", "description": "Task title (1-200 chars)"},
            "description": {"type": "string", "description": "Optional task description"},
            "priority": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "default": "medium",
                "description": "Task priority"
            },
            "category": {
                "type": "string",
                "enum": ["work", "home", "study", "personal", "shopping", "health", "fitness"],
                "description": "Task category (optional)"
            },
            "due_date": {
                "type": "string",
                "description": "Due date in ISO format (optional)"
            }
        },
        "required": ["user_id", "title"]
    }
},

# Update list_tasks definition similarly...
```

---

## 6. Phase 5: Update AI Agent

### Step 1: Update System Prompt

Edit `backend/src/api/services/chat_service.py` and update the system prompt:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant managing a user's todo list.

Available Tools:
1. add_task: Create new task (supports title, description, priority, category, due_date)
2. list_tasks: List tasks (supports filtering, search, sorting)
3. update_task: Update existing task (supports all fields)
4. complete_task: Mark task as completed
5. delete_task: Delete task permanently

TASK FIELDS:
- title (required): Task name
- description (optional): Task details
- priority (optional): high, medium (default), low
- category (optional): work, home, study, personal, shopping, health, fitness
- due_date (optional): ISO datetime string

NATURAL LANGUAGE PARSING:

Priority extraction:
- "urgent", "important", "critical", "asap", "high priority" → high
- "normal", "regular", "medium priority" → medium
- "later", "whenever", "low priority", "not urgent" → low

Category extraction:
- "work", "job", "office", "meeting", "project" → work
- "home", "house", "personal", "chores" → home
- "study", "school", "learning", "homework", "exam" → study
- "shopping", "groceries", "buy", "purchase" → shopping
- "health", "doctor", "medical", "checkup" → health
- "fitness", "gym", "exercise", "workout" → fitness

Due date extraction:
- "today", "tonight" → due end of today
- "tomorrow" → due tomorrow
- "next week" → due in 7 days
- "next Monday", "this Friday" → parse specific day
- "January 15", "Jan 15th", "15th Jan" → parse specific date
- "in 3 days", "in 2 weeks" → calculate relative date

FILTERING & SORTING:

When user asks to filter or search:
- "show high priority tasks" → priority=high
- "list my work tasks" → category=work
- "find tasks with groceries" → search="groceries"
- "tasks due this week" → due_date_from=today, due_date_to=end_of_week
- "show completed tasks" → status=completed

When user asks to sort:
- "sort by due date" → sort_by=due_date
- "sort by priority" → sort_by=priority
- "sort alphabetically" → sort_by=title
- Add sort_order=asc or desc as appropriate

EXAMPLES:

User: "Add high priority work task to finish Q4 report due next Friday"
Action: add_task(title="Finish Q4 report", priority="high", category="work", due_date="2025-01-10T17:00:00Z")

User: "Show me all high priority tasks"
Action: list_tasks(priority="high")

User: "What are my work tasks due this week?"
Action: list_tasks(category="work", due_date_from="2025-12-30", due_date_to="2026-01-05")

User: "Find tasks about groceries"
Action: list_tasks(search="groceries")

User: "Sort my tasks by due date"
Action: list_tasks(sort_by="due_date", sort_order="asc")

RESPONSE FORMAT:
- For add_task: "✅ Added [task] (Task #[id]) - Priority: [priority], Category: [category], Due: [date]"
- For list_tasks with results: Show tasks in a formatted list with priority/category/due date
- For list_tasks empty: "You don't have any tasks matching those filters."
- Always be friendly and conversational
"""
```

---

## 7. Phase 6: Frontend Integration (Optional)

### Option A: Chat-Only (No Code Changes)

The chat interface already works! The AI agent will parse natural language and use the new features automatically.

**Test it**:
- "Add high priority work task to prepare slides due tomorrow"
- "Show me my high priority tasks"
- "List work tasks due this week"

### Option B: Add Visual Task Management UI

Create `frontend/src/components/TaskFilters.tsx`:

```tsx
import React, { useState } from 'react';

interface TaskFiltersProps {
  onFilterChange: (filters: TaskFilters) => void;
}

interface TaskFilters {
  priority?: string;
  category?: string;
  search?: string;
  sortBy?: string;
}

export function TaskFilters({ onFilterChange }: TaskFiltersProps) {
  const [priority, setPriority] = useState('');
  const [category, setCategory] = useState('');
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');

  const handleChange = () => {
    onFilterChange({
      priority: priority || undefined,
      category: category || undefined,
      search: search || undefined,
      sortBy,
    });
  };

  return (
    <div style={{ padding: '1rem', background: '#f9fafb', borderRadius: '0.5rem', marginBottom: '1rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <input
          type="text"
          placeholder="🔍 Search tasks..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); handleChange(); }}
          style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
        />

        <select
          value={priority}
          onChange={(e) => { setPriority(e.target.value); handleChange(); }}
          style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
        >
          <option value="">All Priorities</option>
          <option value="high">🔴 High</option>
          <option value="medium">🟡 Medium</option>
          <option value="low">🟢 Low</option>
        </select>

        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); handleChange(); }}
          style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
        >
          <option value="">All Categories</option>
          <option value="work">💼 Work</option>
          <option value="home">🏠 Home</option>
          <option value="study">📚 Study</option>
          <option value="personal">👤 Personal</option>
          <option value="shopping">🛒 Shopping</option>
          <option value="health">❤️ Health</option>
          <option value="fitness">💪 Fitness</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => { setSortBy(e.target.value); handleChange(); }}
          style={{ padding: '0.5rem', border: '1px solid #d1d5db', borderRadius: '0.375rem' }}
        >
          <option value="created_at">Sort by: Date Created</option>
          <option value="due_date">Sort by: Due Date</option>
          <option value="priority">Sort by: Priority</option>
          <option value="title">Sort by: Title (A-Z)</option>
        </select>
      </div>
    </div>
  );
}
```

---

## 8. Phase 7: Testing

### Test 1: Backward Compatibility

```bash
# Test old API still works (without new fields)
curl -X POST http://localhost:8000/api/demo-user/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task to test backward compatibility"}'

# Should create task with priority=medium, category=null, due_date=null
```

### Test 2: Create Task with Priority

**Chat Message**: "Add high priority task to fix critical bug"

**Expected Response**: ✅ Added 'fix critical bug' (Task #X) - Priority: high

### Test 3: Create Task with Category

**Chat Message**: "Add work task to prepare presentation"

**Expected Response**: ✅ Added 'prepare presentation' (Task #X) - Category: work

### Test 4: Create Task with Due Date

**Chat Message**: "Add task due tomorrow to call dentist"

**Expected Response**: ✅ Added 'call dentist' (Task #X) - Due: 2025-12-31

### Test 5: Filter by Priority

**Chat Message**: "Show me all high priority tasks"

**Expected Response**: List of tasks filtered by priority=high

### Test 6: Filter by Category

**Chat Message**: "List my work tasks"

**Expected Response**: List of tasks filtered by category=work

### Test 7: Search

**Chat Message**: "Find tasks with 'report'"

**Expected Response**: Tasks containing "report" in title or description

### Test 8: Sort by Due Date

**Chat Message**: "Sort my tasks by due date"

**Expected Response**: Tasks sorted by due_date ascending

### Test 9: Complex Filter

**Chat Message**: "Show high priority work tasks due this week"

**Expected Response**: Tasks filtered by priority=high, category=work, due_date in current week

### Test 10: Update Task

**Chat Message**: "Change task 5 to high priority"

**Expected Response**: ✅ Updated task #5 - Priority set to high

---

## Troubleshooting

### Issue: Migration fails

**Solution**:
```bash
# Check migration file syntax
alembic check

# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

### Issue: Validation errors for priority/category

**Solution**: Check that values match exactly: "high" not "High", "work" not "Work"

### Issue: Due date not parsing

**Solution**: Ensure ISO format: `2025-01-15T10:00:00Z` or `2025-01-15T10:00:00+00:00`

### Issue: Search not working

**Solution**: Verify `ilike` is supported (PostgreSQL). For SQLite, use `like`.

### Issue: Sorting by priority not working

**Solution**: Verify the `case` expression for custom priority ordering

---

## Next Steps

1. **Review this implementation guide**
2. **Begin implementation** (follow steps 1-7)
3. **Test thoroughly** (all 10 test scenarios)
4. **Deploy to production** (after testing passes)

**Estimated Total Time**: 6-8 hours

---

**Questions?** Refer to `spec.md` for detailed requirements or ask the AI assistant for clarification.
