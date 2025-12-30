# Agent Skills for Todo Operations

## Overview

Agent Skills are reusable, modular AI capabilities that enhance task management. They can be invoked through the chat interface, API endpoints, or composed together for complex workflows.

## What are Agent Skills?

Agent Skills are **stateless, composable units** that perform specific AI-powered operations on tasks:

- 🔍 **Extract Tasks**: Parse natural language to find actionable items
- 🎯 **Prioritize**: Intelligently assign priority based on context
- 📅 **Schedule**: Suggest optimal due dates and times
- 🏷️ **Categorize**: Auto-assign categories (work, home, shopping, etc.)
- 📋 **Break Down**: Split complex tasks into subtasks

## Quick Start

### Via Chat
```
User: "Extract tasks from: Buy milk, call dentist, finish report"
Agent: Found 3 tasks:
  1. Buy milk
  2. Call dentist
  3. Finish report

  Add these to your list?
```

### Via API
```bash
# Extract tasks
POST /api/{user_id}/skills/extract_tasks
{
  "input": {
    "text": "Buy milk, call dentist, finish report"
  }
}

# Response
{
  "success": true,
  "output": {
    "tasks": [
      {"title": "Buy milk", "confidence": 0.95},
      {"title": "Call dentist", "confidence": 0.90},
      {"title": "Finish report", "confidence": 0.92}
    ]
  }
}
```

## Core Skills

### 1. Task Extraction (`extract_tasks`)
Extract one or more tasks from natural language text.

**Use Cases**:
- Parse email into tasks
- Convert meeting notes to action items
- Extract todos from documents

**Example**:
```
Input: "Tomorrow I need to buy groceries and call John about the project"
Output: ["Buy groceries", "Call John about the project"]
```

### 2. Smart Prioritization (`prioritize_task`)
Assign priority (high/medium/low) based on keywords, deadlines, and context.

**Heuristics**:
- Keywords: "urgent", "critical" → high priority
- Deadline < 24h → high priority
- Work tasks with deadlines → boost priority

**Example**:
```
Input: {title: "Urgent: Fix production bug", category: "work"}
Output: {priority: "high", reasoning: "Contains 'urgent' keyword"}
```

### 3. Intelligent Scheduling (`suggest_schedule`)
Suggest optimal due dates and times based on task characteristics.

**Heuristics**:
- "standup", "meeting" → morning
- "review", "plan" → evening
- Work tasks → business hours
- Health tasks → morning

**Example**:
```
Input: {title: "Morning standup", category: "work"}
Output: {
  suggested_due_date: "2025-01-02T09:00:00Z",
  time_of_day: "morning"
}
```

### 4. Category Classification (`classify_category`)
Auto-assign category based on task title and description.

**Categories**: work, home, study, personal, shopping, health, fitness

**Example**:
```
Input: {title: "Buy groceries for dinner"}
Output: {category: "shopping", confidence: 0.92}
```

### 5. Task Breakdown (`breakdown_task`)
Split complex tasks into smaller, actionable subtasks.

**Example**:
```
Input: {title: "Deploy new feature"}
Output: [
  "Run all tests",
  "Create pull request",
  "Get code review",
  "Merge to main",
  "Deploy to production"
]
```

## Architecture

```
┌─────────────────────────────────────────┐
│          User Interface                 │
│  (Chat Agent or API Client)             │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Skill Executor                    │
│  - Input validation                     │
│  - Skill invocation                     │
│  - Output validation                    │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Skill Registry                    │
│  - extract_tasks                        │
│  - prioritize_task                      │
│  - suggest_schedule                     │
│  - classify_category                    │
│  - breakdown_task                       │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│       Individual Skills                 │
│  (Stateless, composable units)          │
└─────────────────────────────────────────┘
```

## Skill Composition

Chain skills together for complex workflows:

```bash
POST /api/{user_id}/skills/chain
{
  "skills": ["extract_tasks", "prioritize_task", "classify_category"],
  "input": {
    "text": "Urgent: finish project report by tomorrow"
  }
}

# Response
{
  "output": {
    "title": "Finish project report",
    "priority": "high",
    "category": "work",
    "due_date": "2025-01-02T23:59:59Z"
  }
}
```

## Integration Points

### 1. Chat Agent
Skills are automatically invoked when relevant:
- User mentions multiple tasks → `extract_tasks`
- User asks "what's important?" → `prioritize_task`
- User says "when should I do this?" → `suggest_schedule`

### 2. API Endpoints
Direct skill invocation via REST API:
- `/api/{user_id}/skills/{skill_name}` - Execute single skill
- `/api/{user_id}/skills/chain` - Execute skill chain
- `/api/{user_id}/skills/{skill_name}/batch` - Apply to multiple tasks

### 3. Batch Operations
Apply skills to existing tasks:
```bash
POST /api/{user_id}/skills/prioritize_task/batch
{
  "task_ids": [1, 2, 3, 4, 5]
}
```

## Benefits

### For Users
- ⚡ **Faster Task Creation**: Extract multiple tasks at once
- 🎯 **Better Prioritization**: AI-powered priority assignment
- 📅 **Smart Scheduling**: Automatic due date suggestions
- 🏷️ **Auto-Organization**: Tasks categorized automatically
- 📋 **Task Management**: Complex tasks broken into steps

### For Developers
- 🔧 **Modularity**: Skills are independent, testable units
- 🔄 **Reusability**: Same skill works everywhere
- 🔗 **Composability**: Chain skills for complex workflows
- 📈 **Extensibility**: Easy to add new skills
- 🧪 **Testability**: Each skill can be unit tested

## File Structure

```
backend/src/skills/
├── __init__.py                 # Package exports
├── base.py                     # Base Skill class
├── registry.py                 # SkillRegistry
├── executor.py                 # SkillExecutor
├── chain.py                    # SkillChain
├── schemas.py                  # Input/Output schemas
│
├── extraction/
│   └── extract_tasks.py        # Task extraction
│
├── enhancement/
│   ├── prioritize_task.py      # Prioritization
│   ├── suggest_schedule.py     # Scheduling
│   └── classify_category.py    # Categorization
│
└── transformation/
    └── breakdown_task.py       # Task breakdown
```

## Next Steps

1. **Read**: `spec.md` for complete specification
2. **Implement**: Follow `IMPLEMENTATION_GUIDE.md`
3. **Reference**: Use `QUICK_REFERENCE.md` for API docs
4. **Test**: Run unit and integration tests

## Example Use Cases

### 1. Email to Tasks
```
Input: Forward email with multiple action items
Agent: Uses extract_tasks skill
Output: 5 tasks added to your list
```

### 2. Smart Task Creation
```
Input: "Add urgent work task: finish Q4 report by Friday"
Agent: Uses extract_tasks + prioritize_task + classify_category + suggest_schedule
Output: Task created with:
  - Title: "Finish Q4 report"
  - Priority: high (urgent keyword)
  - Category: work
  - Due: 2025-01-03T17:00:00Z (Friday 5pm)
```

### 3. Batch Prioritization
```
Input: "Prioritize all my pending tasks"
Agent: Uses prioritize_task skill in batch mode
Output: All pending tasks re-prioritized based on AI heuristics
```

### 4. Project Planning
```
Input: "Break down 'Launch new product' into steps"
Agent: Uses breakdown_task skill
Output: 8 subtasks created with dependencies
```

## Documentation

- **spec.md**: Complete specification with architecture and algorithms
- **IMPLEMENTATION_GUIDE.md**: Step-by-step implementation instructions
- **QUICK_REFERENCE.md**: API reference and skill catalog
- **README.md**: This file - overview and quick start

---

**Version**: 1.0
**Last Updated**: 2025-12-30
