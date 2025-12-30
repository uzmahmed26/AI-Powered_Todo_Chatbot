# Quick Reference: Todo System Upgrade

## Database Schema Changes

### New Columns in `tasks` Table

| Column | Type | Nullable | Default | Index | Description |
|--------|------|----------|---------|-------|-------------|
| `priority` | VARCHAR(20) | NO | 'medium' | YES | Task priority: high, medium, low |
| `category` | VARCHAR(50) | YES | NULL | YES | Task category: work, home, study, personal, shopping, health, fitness |
| `due_date` | TIMESTAMP WITH TIME ZONE | YES | NULL | YES | Task due date (optional) |

### New Indexes

- `idx_task_priority` on `priority`
- `idx_task_category` on `category`
- `idx_task_due_date` on `due_date`
- `idx_task_user_status_priority` on `(user_id, completed, priority)` - composite

---

## API Changes

### 1. add_task Tool

**New Parameters** (all optional):
```json
{
  "priority": "medium",  // "high" | "medium" | "low"
  "category": null,      // "work" | "home" | "study" | "personal" | "shopping" | "health" | "fitness" | null
  "due_date": null       // ISO datetime string | null
}
```

**Example Request**:
```json
{
  "user_id": "uuid-123",
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "priority": "high",
  "category": "shopping",
  "due_date": "2025-01-15T10:00:00Z"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "task_id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "status": "pending",
    "priority": "high",
    "category": "shopping",
    "due_date": "2025-01-15T10:00:00Z",
    "created_at": "2025-12-30T10:30:00Z",
    "updated_at": "2025-12-30T10:30:00Z"
  },
  "message": "Task created successfully"
}
```

### 2. update_task Tool

**New Parameters** (all optional):
```json
{
  "priority": "high",       // Update priority
  "category": "work",       // Update category
  "due_date": "2025-01-20"  // Update due date
}
```

**Example**:
```json
{
  "user_id": "uuid-123",
  "task_id": 5,
  "priority": "high",
  "category": "work"
}
```

### 3. list_tasks Tool - MAJOR ENHANCEMENT

**New Parameters**:
```json
{
  "priority": null,          // Filter: "high" | "medium" | "low" | null
  "category": null,          // Filter: category name | null
  "search": null,            // Search keyword (title + description)
  "due_date_from": null,     // Filter: ISO datetime string | null
  "due_date_to": null,       // Filter: ISO datetime string | null
  "sort_by": "created_at",   // "created_at" | "due_date" | "priority" | "title"
  "sort_order": "desc"       // "asc" | "desc"
}
```

**Example Request**:
```json
{
  "user_id": "uuid-123",
  "status": "pending",
  "priority": "high",
  "category": "work",
  "sort_by": "due_date",
  "sort_order": "asc"
}
```

**Example Response**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "task_id": 1,
        "title": "Finish Q4 report",
        "description": "Complete all sections",
        "status": "pending",
        "priority": "high",
        "category": "work",
        "due_date": "2025-01-10T17:00:00Z",
        "created_at": "2025-12-30T10:30:00Z",
        "updated_at": "2025-12-30T10:30:00Z"
      }
    ],
    "count": 1,
    "filters": {
      "status": "pending",
      "priority": "high",
      "category": "work",
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

---

## Natural Language Examples

### Priority Extraction

| User Says | Extracted Priority |
|-----------|-------------------|
| "Add urgent task..." | high |
| "Create important task..." | high |
| "Add critical task..." | high |
| "Add normal task..." | medium |
| "Add regular task..." | medium |
| "Add low priority task..." | low |
| "Add task for later..." | low |

### Category Extraction

| User Says | Extracted Category |
|-----------|-------------------|
| "Add work task..." | work |
| "Create job task..." | work |
| "Add office task..." | work |
| "Add home task..." | home |
| "Create house task..." | home |
| "Add study task..." | study |
| "Create homework..." | study |
| "Add shopping task..." | shopping |
| "Buy groceries..." | shopping |
| "Add health task..." | health |
| "Schedule doctor..." | health |
| "Add fitness task..." | fitness |
| "Go to gym..." | fitness |

### Due Date Extraction

| User Says | Parsed Due Date |
|-----------|----------------|
| "...due today" | End of today (23:59) |
| "...due tonight" | End of today (23:59) |
| "...due tomorrow" | Tomorrow at noon |
| "...due next week" | 7 days from now |
| "...due next Monday" | Next Monday at noon |
| "...due January 15" | Jan 15, current year |
| "...due in 3 days" | 3 days from now |

### Filtering Examples

| User Says | MCP Tool Call |
|-----------|--------------|
| "Show high priority tasks" | `list_tasks(priority="high")` |
| "List my work tasks" | `list_tasks(category="work")` |
| "Show completed tasks" | `list_tasks(status="completed")` |
| "Find tasks with groceries" | `list_tasks(search="groceries")` |
| "Tasks due this week" | `list_tasks(due_date_from="...", due_date_to="...")` |
| "Show high priority work tasks" | `list_tasks(priority="high", category="work")` |

### Sorting Examples

| User Says | MCP Tool Call |
|-----------|--------------|
| "Sort by due date" | `list_tasks(sort_by="due_date", sort_order="asc")` |
| "Sort by priority" | `list_tasks(sort_by="priority")` |
| "Sort alphabetically" | `list_tasks(sort_by="title", sort_order="asc")` |
| "Show newest first" | `list_tasks(sort_by="created_at", sort_order="desc")` |

---

## Migration Command

```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 002 -> 003, add task enhancements
```

---

## Validation Rules

### Priority
- **Valid values**: "high", "medium", "low"
- **Default**: "medium"
- **Case-sensitive**: lowercase only

### Category
- **Valid values**: "work", "home", "study", "personal", "shopping", "health", "fitness", null
- **Default**: null (no category)
- **Case-sensitive**: lowercase only

### Due Date
- **Format**: ISO 8601 datetime string
- **Examples**:
  - `2025-01-15T10:00:00Z`
  - `2025-01-15T10:00:00+00:00`
  - `2025-01-15T10:00:00-05:00`
- **Default**: null (no due date)

---

## Testing Checklist

- [ ] **Backward compatibility**: Old add_task calls work without new fields
- [ ] **Create with priority**: "Add high priority task to fix bug"
- [ ] **Create with category**: "Add work task to prepare slides"
- [ ] **Create with due date**: "Add task due tomorrow to call dentist"
- [ ] **Filter by priority**: "Show high priority tasks"
- [ ] **Filter by category**: "List work tasks"
- [ ] **Search**: "Find tasks with 'report'"
- [ ] **Sort by due date**: "Sort tasks by due date"
- [ ] **Sort by priority**: "Sort by priority"
- [ ] **Complex filter**: "Show high priority work tasks due this week"
- [ ] **Update priority**: "Change task 5 to low priority"
- [ ] **Update category**: "Set task 3 to home category"
- [ ] **Existing tasks have defaults**: priority=medium, category=null

---

## Frontend Integration (Optional)

### Task Card Display

```tsx
<div className="task-card">
  {/* Priority badge */}
  <span className={`badge priority-${task.priority}`}>
    {task.priority === 'high' ? '🔴' : task.priority === 'medium' ? '🟡' : '🟢'}
    {task.priority.toUpperCase()}
  </span>

  {/* Category badge */}
  {task.category && (
    <span className="badge category">
      {getCategoryIcon(task.category)} {task.category}
    </span>
  )}

  {/* Task content */}
  <h3>{task.title}</h3>
  <p>{task.description}</p>

  {/* Due date */}
  {task.due_date && (
    <div className={`due-date ${isOverdue(task.due_date) ? 'overdue' : ''}`}>
      📅 Due: {formatDate(task.due_date)}
    </div>
  )}
</div>
```

### Category Icons

```tsx
function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    work: '💼',
    home: '🏠',
    study: '📚',
    personal: '👤',
    shopping: '🛒',
    health: '❤️',
    fitness: '💪',
  };
  return icons[category] || '📝';
}
```

### CSS Priority Colors

```css
.priority-high {
  background: #fee2e2;
  color: #dc2626;
  border-left: 4px solid #dc2626;
}

.priority-medium {
  background: #fef3c7;
  color: #d97706;
  border-left: 4px solid #d97706;
}

.priority-low {
  background: #dcfce7;
  color: #16a34a;
  border-left: 4px solid #16a34a;
}

.due-date.overdue {
  color: #dc2626;
  font-weight: bold;
}
```

---

## Rollback (if needed)

```bash
cd backend
alembic downgrade -1
```

This will remove the new columns and indexes.

---

## Performance Notes

- All new fields are indexed for fast filtering
- Composite index `(user_id, completed, priority)` optimizes common queries
- Search uses `ILIKE` which is slower but acceptable for small datasets
- For large datasets (>10,000 tasks per user), consider full-text search

---

## Security Notes

- User isolation maintained (all queries filter by user_id)
- Enum validation prevents SQL injection
- Date parsing uses safe ISO format
- No user input is executed or evaluated

---

**For detailed implementation steps, see**: `IMPLEMENTATION_GUIDE.md`
**For complete specification, see**: `spec.md`
