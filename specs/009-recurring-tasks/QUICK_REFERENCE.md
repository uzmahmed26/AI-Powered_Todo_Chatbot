# Quick Reference: Recurring Tasks

## Database Schema Changes

### New Columns in `tasks` Table

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `is_recurring` | BOOLEAN | NO | FALSE | Whether task recurs |
| `recurrence_pattern` | VARCHAR(20) | YES | NULL | daily, weekly, monthly |
| `recurrence_interval` | INTEGER | NO | 1 | Recurrence frequency (e.g., every 2 weeks) |
| `recurrence_end_date` | TIMESTAMP TZ | YES | NULL | When recurrence ends (optional) |
| `recurrence_day_of_week` | INTEGER | YES | NULL | 0-6 for weekly (0=Monday) |
| `recurrence_day_of_month` | INTEGER | YES | NULL | 1-31 for monthly |
| `parent_recurrence_id` | INTEGER | YES | NULL | Links to original recurring task |
| `recurrence_active` | BOOLEAN | NO | TRUE | Whether recurrence is active |

### Indexes

- `idx_task_is_recurring` on `is_recurring`
- `idx_task_recurrence_active` on `recurrence_active`
- `idx_task_parent_recurrence` on `parent_recurrence_id`

---

## Recurrence Patterns

### Daily
- Pattern: `"daily"`
- Next due: current due + 1 day (or interval days)
- Example: "Every day at 9am"

### Weekly
- Pattern: `"weekly"`
- Day of week: 0=Monday, 1=Tuesday, ..., 6=Sunday
- Next due: Next occurrence of specified weekday
- Example: "Every Monday at 5pm"

### Monthly
- Pattern: `"monthly"`
- Day of month: 1-31
- Next due: Same day next month (handles month-end overflow)
- Example: "1st of every month"

---

## API Changes

### add_task Tool

**New Parameters**:
```json
{
  "is_recurring": false,
  "recurrence_pattern": null,        // "daily" | "weekly" | "monthly"
  "recurrence_interval": 1,           // Every N days/weeks/months
  "recurrence_end_date": null,        // ISO datetime
  "recurrence_day_of_week": null,     // 0-6 for weekly
  "recurrence_day_of_month": null     // 1-31 for monthly
}
```

**Example - Daily**:
```json
{
  "title": "Check email",
  "is_recurring": true,
  "recurrence_pattern": "daily",
  "due_date": "2025-12-31T09:00:00Z"
}
```

**Example - Weekly (every Monday)**:
```json
{
  "title": "Submit timesheet",
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_day_of_week": 0,
  "due_date": "2026-01-06T17:00:00Z"
}
```

**Example - Monthly (1st of month)**:
```json
{
  "title": "Pay rent",
  "is_recurring": true,
  "recurrence_pattern": "monthly",
  "recurrence_day_of_month": 1,
  "due_date": "2026-01-01T00:00:00Z"
}
```

### complete_task Tool

**Enhanced Response**:
```json
{
  "success": true,
  "data": {...},
  "message": "Task completed. Next instance created for Jan 1, 2026",
  "next_task_id": 123
}
```

### update_task Tool

**New Parameters**:
```json
{
  "recurrence_active": true,    // Pause/resume
  "recurrence_end_date": "..."  // Extend/shorten
}
```

### list_tasks Tool

**New Filters**:
```json
{
  "is_recurring": true,          // Show only recurring
  "show_recurring_only": true    // Show templates only
}
```

### stop_recurrence Tool (New)

**Purpose**: Stop all future instances

```json
// Request
{
  "user_id": "uuid-123",
  "task_id": 5
}

// Response
{
  "success": true,
  "message": "Recurrence stopped for 'check email'. Existing task remains."
}
```

---

## Natural Language Examples

### Creating Recurring Tasks

| User Says | Extracted Fields |
|-----------|-----------------|
| "Remind me to check email every day" | `is_recurring=true`, `recurrence_pattern="daily"` |
| "Add recurring task every Monday to submit timesheet" | `recurrence_pattern="weekly"`, `recurrence_day_of_week=0` |
| "Pay rent on the 1st of every month" | `recurrence_pattern="monthly"`, `recurrence_day_of_month=1` |
| "Daily task to exercise at 7am" | `recurrence_pattern="daily"`, extract time from "7am" |
| "Every Friday review tasks" | `recurrence_pattern="weekly"`, `recurrence_day_of_week=4` |

### Managing Recurring Tasks

| User Says | Action |
|-----------|--------|
| "Stop the daily email reminder" | Find task, call `stop_recurrence` |
| "Cancel recurring timesheet task" | `stop_recurrence` |
| "Show my recurring tasks" | `list_tasks(is_recurring=true)` |
| "Pause the gym reminder" | `update_task(recurrence_active=false)` |

---

## Recurrence Logic

### Calculate Next Due Date

**Daily**:
```python
next_date = current_due_date + timedelta(days=interval)
```

**Weekly**:
```python
# Find next occurrence of weekday
days_ahead = target_weekday - current_date.weekday()
if days_ahead <= 0:
    days_ahead += 7
next_date = current_date + timedelta(days=days_ahead)
```

**Monthly**:
```python
next_month = (current_month + interval) % 12
next_year = current_year + ((current_month + interval) // 12)

try:
    next_date = datetime(next_year, next_month, day_of_month)
except ValueError:
    # Day doesn't exist (e.g., Feb 31), use last day of month
    next_date = datetime(next_year, next_month, last_day_of_month)
```

### Task Generation on Completion

```python
def on_task_complete(task):
    if not task.is_recurring or not task.recurrence_active:
        return

    # Check if recurrence should end
    if task.recurrence_end_date and now() >= task.recurrence_end_date:
        logger.info("Recurrence ended")
        return

    # Create next instance
    next_task = Task(
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        category=task.category,
        due_date=calculate_next_due_date(task),
        completed=False,

        # Copy recurrence settings
        is_recurring=True,
        recurrence_pattern=task.recurrence_pattern,
        recurrence_interval=task.recurrence_interval,
        recurrence_end_date=task.recurrence_end_date,
        recurrence_day_of_week=task.recurrence_day_of_week,
        recurrence_day_of_month=task.recurrence_day_of_month,
        parent_recurrence_id=task.parent_recurrence_id or task.id,
        recurrence_active=True
    )

    db.add(next_task)
    db.commit()
```

---

## Background Scheduler

### APScheduler Setup

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

scheduler.add_job(
    check_recurring_tasks,
    trigger=IntervalTrigger(hours=1),
    id="recurrence_check"
)

scheduler.start()
```

### Scheduler Job

```python
async def check_recurring_tasks():
    """Check for completed recurring tasks without next instance."""

    # Find completed recurring tasks
    tasks = await db.query(Task).filter(
        Task.is_recurring == True,
        Task.recurrence_active == True,
        Task.completed == True
    ).all()

    for task in tasks:
        # Check if next instance exists
        next_exists = await check_next_instance_exists(task)

        if not next_exists:
            # Create next instance
            create_next_recurrence_instance(task)
```

---

## Frontend Integration

### Recurring Task Badge

```tsx
{task.is_recurring && (
  <span className="recurring-badge">
    🔄 {formatRecurrence(task)}
  </span>
)}

function formatRecurrence(task) {
  switch (task.recurrence_pattern) {
    case 'daily':
      return 'Daily';
    case 'weekly':
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      return `Weekly (${days[task.recurrence_day_of_week]})`;
    case 'monthly':
      return `Monthly (${task.recurrence_day_of_month}${getDaySuffix(task.recurrence_day_of_month)})`;
    default:
      return 'Recurring';
  }
}
```

### Stop Recurrence Button

```tsx
{task.is_recurring && task.recurrence_active && (
  <button onClick={() => stopRecurrence(task.id)}>
    Stop Recurrence
  </button>
)}

async function stopRecurrence(taskId) {
  await apiClient.stopRecurrence(taskId);
  refreshTasks();
}
```

---

## Migration Command

```bash
cd backend
python -m alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade 003 -> 004, add recurring tasks support
```

---

## Validation Rules

### Recurrence Pattern
- **Valid values**: "daily", "weekly", "monthly"
- **Required if**: `is_recurring=true`

### Recurrence Interval
- **Type**: Integer
- **Range**: >= 1
- **Default**: 1

### Day of Week (weekly only)
- **Type**: Integer
- **Range**: 0-6 (0=Monday, 6=Sunday)
- **Required**: Recommended for weekly recurrence

### Day of Month (monthly only)
- **Type**: Integer
- **Range**: 1-31
- **Handles overflow**: Feb 31 → Feb 28/29

### End Date
- **Type**: ISO datetime string
- **Validation**: Must be in future
- **Optional**: Recurrence continues indefinitely if not set

---

## Testing Checklist

- [ ] **Create daily recurring task**
- [ ] **Create weekly recurring task (specific day)**
- [ ] **Create monthly recurring task (specific date)**
- [ ] **Complete recurring task → next instance created**
- [ ] **Recurrence respects end date**
- [ ] **Stop recurrence → no more instances**
- [ ] **Pause/resume recurrence**
- [ ] **Month-end handling (31st → last day of month)**
- [ ] **Scheduler creates missed instances**
- [ ] **Natural language: "every day" → daily**
- [ ] **Natural language: "every Monday" → weekly**
- [ ] **Natural language: "1st of month" → monthly**

---

## Common Patterns

### Every Day at 9am
```json
{
  "is_recurring": true,
  "recurrence_pattern": "daily",
  "due_date": "2025-12-31T09:00:00Z"
}
```

### Every Monday at 5pm
```json
{
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_day_of_week": 0,
  "due_date": "2026-01-06T17:00:00Z"
}
```

### 1st of Every Month
```json
{
  "is_recurring": true,
  "recurrence_pattern": "monthly",
  "recurrence_day_of_month": 1,
  "due_date": "2026-01-01T00:00:00Z"
}
```

### Every 2 Weeks
```json
{
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_interval": 2,
  "due_date": "2026-01-06T12:00:00Z"
}
```

---

## Troubleshooting

### Issue: Next instance not created after completion

**Solution**:
1. Check `recurrence_active=true`
2. Check `recurrence_end_date` not passed
3. Run scheduler manually: wait for hourly check
4. Check logs for errors

### Issue: Duplicate tasks created

**Solution**:
1. Enable distributed locking (Redis)
2. Check scheduler running only once
3. Verify `parent_recurrence_id` linking

### Issue: Monthly recurrence on 31st fails

**Solution**:
- System automatically uses last day of month for months without 31 days
- Feb 31 → Feb 28 (or 29 in leap years)
- This is expected behavior

---

**For detailed implementation steps, see**: `IMPLEMENTATION_GUIDE.md`
**For complete specification, see**: `spec.md`
