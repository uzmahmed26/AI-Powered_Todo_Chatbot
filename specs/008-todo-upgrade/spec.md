# Feature Specification: Todo System Upgrade

**Feature ID**: 008-todo-upgrade
**Status**: Planning
**Created**: 2025-12-30
**Priority**: High

## 1. Overview

Upgrade the existing Todo system to include priority levels, categories/tags, search functionality, and advanced filtering/sorting capabilities while maintaining backward compatibility with existing APIs.

### 1.1 Success Criteria

- ✅ Add priority field (high/medium/low) to tasks
- ✅ Add category/tag support (work/home/study)
- ✅ Add due_date field with datetime support
- ✅ Implement keyword search across title and description
- ✅ Implement filtering by completion status, priority, category, and due date
- ✅ Implement sorting by due date, priority, alphabetical (title)
- ✅ Maintain backward compatibility with existing APIs
- ✅ Update all MCP tools to support new fields
- ✅ Add new list_tasks parameters for filtering/sorting
- ✅ Update frontend to use new features

### 1.2 Non-Goals

- Task attachments or file uploads
- Task dependencies or subtasks
- Task reminders or notifications
- Recurring tasks
- Task sharing between users
- Custom categories (predefined set only)

## 2. User Stories

### 2.1 As a user, I want to set priority levels on tasks

**Acceptance Criteria**:
- Can set priority when creating a task: "Add high priority task to buy groceries"
- Can update priority: "Set task 5 to low priority"
- Can filter by priority: "Show me all high priority tasks"
- Priority defaults to "medium" if not specified
- Valid values: high, medium, low

### 2.2 As a user, I want to categorize tasks

**Acceptance Criteria**:
- Can set category when creating: "Add work task to finish report"
- Can update category: "Change task 3 to home category"
- Can filter by category: "Show me all work tasks"
- Category is optional (can be null)
- Valid values: work, home, study, personal, shopping, health, fitness

### 2.3 As a user, I want to set due dates

**Acceptance Criteria**:
- Can set due date: "Add task due tomorrow to call dentist"
- Can set specific dates: "Add task due on January 15th"
- Can update due date: "Change task 2 due date to next week"
- Can filter by due date: "Show tasks due this week"
- Due date is optional

### 2.4 As a user, I want to search tasks

**Acceptance Criteria**:
- Can search by keyword: "Find tasks with 'groceries'"
- Search looks in title and description
- Search is case-insensitive
- Returns partial matches

### 2.5 As a user, I want to filter and sort tasks

**Acceptance Criteria**:
- Can filter by multiple criteria: "Show high priority work tasks"
- Can sort by due date: "Sort my tasks by due date"
- Can sort by priority: "Show tasks sorted by priority"
- Can sort alphabetically: "List tasks alphabetically"

## 3. Database Schema Changes

### 3.1 Task Model Updates

**New Fields**:
```python
class Task(SQLModel, table=True):
    # ... existing fields ...

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
```

**Indexes to Add**:
- `idx_task_priority` on `priority`
- `idx_task_category` on `category`
- `idx_task_due_date` on `due_date`
- Composite index: `idx_task_user_status_priority` on `(user_id, completed, priority)`

### 3.2 Migration Strategy

**Approach**: Add nullable columns with defaults, maintain backward compatibility

1. Create new migration: `003_add_task_enhancements.py`
2. Add priority column with default "medium"
3. Add category column (nullable)
4. Add due_date column (nullable)
5. Create indexes
6. Existing tasks will automatically have priority="medium", category=null, due_date=null

## 4. API Changes

### 4.1 Backward Compatibility Rules

- All existing API calls continue to work without modification
- New fields are optional in requests
- New fields are always included in responses (with defaults for old data)
- MCP tools accept but don't require new parameters

### 4.2 MCP Tool Updates

#### 4.2.1 add_task Tool

**Current Signature**:
```python
async def execute(user_id: str, title: str, description: str = None)
```

**New Signature**:
```python
async def execute(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",  # NEW (optional)
    category: str = None,      # NEW (optional)
    due_date: str = None       # NEW (optional, ISO format)
)
```

**Validation**:
- priority must be one of: "high", "medium", "low"
- category must be one of: "work", "home", "study", "personal", "shopping", "health", "fitness", or null
- due_date must be valid ISO datetime string or null

**Response Updates**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "status": "pending",
    "priority": "high",      // NEW
    "category": "shopping",  // NEW
    "due_date": "2025-01-15T10:00:00Z",  // NEW
    "created_at": "2025-12-30T10:30:00Z",
    "updated_at": "2025-12-30T10:30:00Z"
  },
  "message": "Task created successfully"
}
```

#### 4.2.2 update_task Tool

**Current Signature**:
```python
async def execute(user_id: str, task_id: int, title: str = None, description: str = None)
```

**New Signature**:
```python
async def execute(
    user_id: str,
    task_id: int,
    title: str = None,
    description: str = None,
    priority: str = None,   # NEW (optional)
    category: str = None,   # NEW (optional)
    due_date: str = None    # NEW (optional)
)
```

#### 4.2.3 list_tasks Tool - MAJOR ENHANCEMENT

**Current Signature**:
```python
async def execute(user_id: str, status: str = "all")
```

**New Signature**:
```python
async def execute(
    user_id: str,
    status: str = "all",           # existing
    priority: str = None,          # NEW filter
    category: str = None,          # NEW filter
    search: str = None,            # NEW search keyword
    due_date_from: str = None,     # NEW filter (ISO date)
    due_date_to: str = None,       # NEW filter (ISO date)
    sort_by: str = "created_at",   # NEW sort field
    sort_order: str = "desc"       # NEW sort direction
)
```

**Sort Options**:
- `sort_by`: "created_at" (default), "due_date", "priority", "title"
- `sort_order`: "asc", "desc" (default)
- Priority sorting: high > medium > low

**Search Behavior**:
- Case-insensitive search in title and description
- Partial matching (ILIKE '%keyword%')

**Response Format** (enhanced):
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "task_id": 1,
        "title": "Buy groceries",
        "description": "Milk, bread, eggs",
        "status": "pending",
        "priority": "high",
        "category": "shopping",
        "due_date": "2025-01-15T10:00:00Z",
        "created_at": "2025-12-30T10:30:00Z",
        "updated_at": "2025-12-30T10:30:00Z"
      }
    ],
    "count": 1,
    "filters": {
      "status": "all",
      "priority": "high",
      "category": null,
      "search": null
    },
    "sort": {
      "by": "due_date",
      "order": "asc"
    }
  },
  "message": "Found 1 task"
}
```

#### 4.2.4 complete_task & delete_task

**No Changes**: These tools remain unchanged, only task_id and user_id required.

### 4.3 AI Agent Prompt Updates

The AI agent system prompt should be updated to understand new capabilities:

```
Available task fields:
- title (required): Task name
- description (optional): Task details
- priority (optional): high, medium (default), low
- category (optional): work, home, study, personal, shopping, health, fitness
- due_date (optional): ISO datetime string

When users mention priority, extract and use it:
- "urgent", "important", "critical" → high
- "normal", "regular" → medium
- "later", "whenever", "low" → low

When users mention categories, extract and use:
- "work", "job", "office" → work
- "home", "house", "personal" → home
- "study", "school", "learning" → study
- "shopping", "groceries", "buy" → shopping
- etc.

When users mention time:
- "today", "tonight" → due today
- "tomorrow" → due tomorrow
- "next week" → due in 7 days
- "Jan 15", "January 15th" → parse specific date

Filtering examples users might say:
- "show high priority tasks" → filter priority=high
- "list my work tasks" → filter category=work
- "tasks due this week" → filter due_date range
- "search for groceries" → search keyword
- "sort by due date" → sort_by=due_date
```

## 5. Frontend Integration

### 5.1 UI Components Needed

#### 5.1.1 Task Creation/Edit Form Enhancements

Add these input fields to task forms:

**Priority Selector**:
```tsx
<select name="priority" defaultValue="medium">
  <option value="high">🔴 High Priority</option>
  <option value="medium">🟡 Medium Priority</option>
  <option value="low">🟢 Low Priority</option>
</select>
```

**Category Selector**:
```tsx
<select name="category">
  <option value="">No Category</option>
  <option value="work">💼 Work</option>
  <option value="home">🏠 Home</option>
  <option value="study">📚 Study</option>
  <option value="personal">👤 Personal</option>
  <option value="shopping">🛒 Shopping</option>
  <option value="health">❤️ Health</option>
  <option value="fitness">💪 Fitness</option>
</select>
```

**Due Date Picker**:
```tsx
<input
  type="datetime-local"
  name="due_date"
  min={new Date().toISOString().slice(0, 16)}
/>
```

#### 5.1.2 Task Display Updates

**Task Card/Item**:
```tsx
<div className="task-item">
  <div className="task-header">
    <span className={`priority-badge priority-${task.priority}`}>
      {task.priority.toUpperCase()}
    </span>
    {task.category && (
      <span className="category-badge">{getCategoryIcon(task.category)} {task.category}</span>
    )}
  </div>
  <h3>{task.title}</h3>
  <p>{task.description}</p>
  {task.due_date && (
    <div className="due-date">
      📅 Due: {formatDueDate(task.due_date)}
    </div>
  )}
</div>
```

#### 5.1.3 Filter & Search Panel

```tsx
<div className="filters-panel">
  <input
    type="text"
    placeholder="🔍 Search tasks..."
    onChange={(e) => setSearchKeyword(e.target.value)}
  />

  <select onChange={(e) => setPriorityFilter(e.target.value)}>
    <option value="">All Priorities</option>
    <option value="high">High</option>
    <option value="medium">Medium</option>
    <option value="low">Low</option>
  </select>

  <select onChange={(e) => setCategoryFilter(e.target.value)}>
    <option value="">All Categories</option>
    <option value="work">Work</option>
    <option value="home">Home</option>
    {/* ... */}
  </select>

  <select onChange={(e) => setSortBy(e.target.value)}>
    <option value="created_at">Sort by Date Created</option>
    <option value="due_date">Sort by Due Date</option>
    <option value="priority">Sort by Priority</option>
    <option value="title">Sort Alphabetically</option>
  </select>
</div>
```

### 5.2 Conversational Interface

The chat interface already handles this automatically via the AI agent:

**User**: "Add high priority work task to finish Q4 report due next Friday"
**AI**: ✅ Creates task with priority=high, category=work, due_date parsed

**User**: "Show my high priority tasks"
**AI**: 📋 Lists tasks filtered by priority=high

**User**: "What are my work tasks due this week?"
**AI**: 📋 Lists tasks filtered by category=work and due_date range

No changes needed in `SmartTodoApp.tsx` - the AI handles natural language parsing.

### 5.3 Optional: Direct Task Management UI

If you want to add a visual task list (beyond chat):

**New Component**: `TaskListView.tsx`
- Grid/list view of tasks
- Filter panel
- Search bar
- Sort controls
- Click to edit task
- Visual priority indicators (colored borders/badges)
- Category icons/badges
- Due date warnings (red if overdue, yellow if due soon)

## 6. Implementation Checklist

### Phase 1: Database & Backend Core (2-3 hours)

- [ ] Create migration `003_add_task_enhancements.py`
- [ ] Update `Task` model in `backend/src/models/task.py`
- [ ] Create validation enums for priority and category
- [ ] Run migration: `alembic upgrade head`
- [ ] Test: Create task with new fields manually

### Phase 2: MCP Tools (2-3 hours)

- [ ] Update `add_task` tool with new parameters
- [ ] Update `update_task` tool with new parameters
- [ ] Update `list_tasks` tool with filtering/sorting
- [ ] Update schemas in `backend/src/mcp_server/schemas.py`
- [ ] Update MCP server tool definitions in `backend/src/mcp_server/server.py`
- [ ] Test: Call tools directly with new parameters

### Phase 3: AI Agent (30 min)

- [ ] Update system prompt in `backend/src/api/services/chat_service.py`
- [ ] Add natural language extraction for priority/category/dates
- [ ] Test: Chat messages with priority/category/dates

### Phase 4: Frontend (Optional) (2-3 hours)

- [ ] Add filter/search UI components
- [ ] Update task display with priority/category/due_date
- [ ] Add priority/category/due_date inputs to forms
- [ ] Test: Create, filter, search tasks via UI

### Phase 5: Testing & Validation (1 hour)

- [ ] Test backward compatibility (old API calls work)
- [ ] Test new features via chat interface
- [ ] Test filtering and sorting
- [ ] Test search functionality
- [ ] Test due date parsing and display
- [ ] Verify existing tasks have defaults (priority=medium)

## 7. Testing Scenarios

### 7.1 Backward Compatibility Tests

1. **Old add_task call works**:
   - Call: `add_task(user_id, "Test task")`
   - Expected: Task created with priority="medium", category=null, due_date=null

2. **Old list_tasks call works**:
   - Call: `list_tasks(user_id, status="all")`
   - Expected: All tasks returned with new fields populated

### 7.2 New Feature Tests

1. **Create task with priority**:
   - Chat: "Add high priority task to fix bug"
   - Expected: Task created with priority="high"

2. **Create task with category**:
   - Chat: "Add work task to prepare presentation"
   - Expected: Task created with category="work"

3. **Create task with due date**:
   - Chat: "Add task due tomorrow to call dentist"
   - Expected: Task created with due_date set to tomorrow

4. **Filter by priority**:
   - Chat: "Show me high priority tasks"
   - Expected: Only high priority tasks returned

5. **Filter by category**:
   - Chat: "List my work tasks"
   - Expected: Only work category tasks returned

6. **Search by keyword**:
   - Chat: "Find tasks with 'report'"
   - Expected: Tasks containing "report" in title or description

7. **Sort by due date**:
   - Chat: "Sort tasks by due date"
   - Expected: Tasks ordered by due_date (earliest first)

8. **Complex filter**:
   - Chat: "Show high priority work tasks due this week"
   - Expected: Tasks filtered by priority=high, category=work, due_date in current week

## 8. Constraints & Assumptions

### 8.1 Constraints

- Must maintain backward compatibility with existing APIs
- Priority limited to 3 levels (high, medium, low)
- Categories are predefined set (no custom categories)
- Due dates use UTC timezone
- Search is simple keyword matching (no advanced full-text search)

### 8.2 Assumptions

- Users primarily interact via chat (conversational AI)
- Direct UI for task management is optional
- AI agent can parse natural language for priority/category/dates
- Existing tasks will have default values (priority="medium")
- Due dates are optional (many tasks don't need deadlines)

## 9. Security Considerations

- All existing user isolation rules remain
- New fields don't introduce security risks
- No user input is executed or evaluated
- Enum validation prevents injection attacks
- Date parsing uses safe libraries

## 10. Performance Considerations

- New indexes added for priority, category, due_date
- Composite index for common query patterns
- Search uses ILIKE which is slower but acceptable for small datasets
- Consider adding full-text search if dataset grows large (>10,000 tasks per user)

## 11. Future Enhancements (Out of Scope)

- Custom categories
- Task attachments
- Recurring tasks
- Task dependencies
- Subtasks
- Task reminders/notifications
- Task sharing
- Task templates
- Bulk operations
- Advanced full-text search
- Task history/audit log

## 12. Rollout Strategy

1. **Phase 1**: Deploy backend changes (database + MCP tools)
2. **Phase 2**: Test via direct API calls
3. **Phase 3**: Deploy AI agent updates
4. **Phase 4**: Test via chat interface
5. **Phase 5**: Deploy frontend UI updates (if applicable)
6. **Phase 6**: Monitor for issues, iterate

## 13. Success Metrics

- All existing tests pass (backward compatibility)
- New feature tests pass
- Users can create tasks with priority/category/due_date
- Users can filter and search tasks
- AI agent correctly extracts priority/category/dates from natural language
- Response times remain under 500ms for list_tasks queries

---

**Next Steps**:
1. Review and approve this specification
2. Generate implementation plan (`plan.md`)
3. Generate task breakdown (`tasks.md`)
4. Begin implementation
