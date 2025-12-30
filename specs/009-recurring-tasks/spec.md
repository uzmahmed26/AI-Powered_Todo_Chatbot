# Feature Specification: Recurring Tasks

**Feature ID**: 009-recurring-tasks
**Status**: Planning
**Created**: 2025-12-30
**Priority**: High
**Dependencies**: 008-todo-upgrade (priority, categories, due dates)

## 1. Overview

Add recurring tasks functionality to enable users to create tasks that automatically regenerate on a schedule (daily, weekly, monthly). When a recurring task is completed, the system automatically creates the next instance with the same attributes.

### 1.1 Success Criteria

- ✅ Support daily, weekly, and monthly recurrence patterns
- ✅ Auto-create next task instance when current task is completed
- ✅ Preserve all task attributes (priority, category, title, description)
- ✅ Allow users to stop/pause recurrence
- ✅ Support recurrence end dates (optional)
- ✅ Scalable, cloud-ready background task processing
- ✅ Natural language parsing for recurrence patterns
- ✅ Frontend UI for managing recurring tasks

### 1.2 Non-Goals

- Complex recurrence patterns (e.g., "every other Tuesday", "last Friday of month")
- Multiple recurrence rules per task
- Modifying past recurrence instances
- Recurrence exceptions (skip specific dates)
- Task series management (viewing all instances of a recurring task)
- Syncing with external calendars

## 2. User Stories

### 2.1 As a user, I want to create daily recurring tasks

**Acceptance Criteria**:
- Can create task with daily recurrence: "Add recurring task to check email every day"
- Task automatically creates next instance when completed
- Recurrence continues indefinitely unless stopped
- Can specify end date: "recurring daily until January 31st"

**Examples**:
- "Remind me to check email every day"
- "Add daily task to exercise"
- "Create daily recurring task to review calendar at 9am"

### 2.2 As a user, I want to create weekly recurring tasks

**Acceptance Criteria**:
- Can create task with weekly recurrence: "Add recurring task to submit timesheet every Monday"
- Task recurs on the same day of week
- Can specify which day: "every Monday", "every Friday"
- Preserves due time if specified

**Examples**:
- "Remind me to submit timesheet every Monday"
- "Add weekly task to grocery shopping on Saturday"
- "Create recurring task every Friday to backup files"

### 2.3 As a user, I want to create monthly recurring tasks

**Acceptance Criteria**:
- Can create task with monthly recurrence: "Add recurring task to pay rent on the 1st"
- Task recurs on the same day of month
- Handles month-end correctly (e.g., 31st becomes last day of month)
- Can specify day of month: "1st", "15th", etc.

**Examples**:
- "Remind me to pay rent on the 1st of every month"
- "Add monthly task to review budget on the 15th"
- "Create recurring task for team meeting every month"

### 2.4 As a user, I want to stop a recurring task

**Acceptance Criteria**:
- Can stop recurrence: "Stop recurring task for email check"
- Existing task remains, but no future instances created
- Can delete recurring task entirely
- Can restart recurrence later

**Examples**:
- "Stop the daily email reminder"
- "Cancel the weekly timesheet task"
- "Remove recurrence from grocery shopping"

### 2.5 As a user, I want recurring tasks to preserve attributes

**Acceptance Criteria**:
- Next instance has same title, description, priority, category
- Due time preserved (e.g., 9am daily becomes 9am next day)
- Task IDs are unique for each instance
- Original task completion doesn't affect next instance

## 3. Database Schema Changes

### 3.1 Task Model Updates

Add recurrence fields to existing `tasks` table:

```sql
-- New columns for recurring tasks
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN recurrence_pattern VARCHAR(20); -- 'daily', 'weekly', 'monthly'
ALTER TABLE tasks ADD COLUMN recurrence_interval INTEGER DEFAULT 1; -- e.g., every 2 weeks
ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN recurrence_day_of_week INTEGER; -- 0-6 for weekly (0=Monday)
ALTER TABLE tasks ADD COLUMN recurrence_day_of_month INTEGER; -- 1-31 for monthly
ALTER TABLE tasks ADD COLUMN parent_recurrence_id INTEGER; -- Links to original recurring task template
ALTER TABLE tasks ADD COLUMN recurrence_active BOOLEAN DEFAULT TRUE; -- Can pause recurrence

-- Indexes
CREATE INDEX idx_task_is_recurring ON tasks(is_recurring);
CREATE INDEX idx_task_recurrence_active ON tasks(recurrence_active);
CREATE INDEX idx_task_parent_recurrence ON tasks(parent_recurrence_id);
```

**SQLModel Definition**:
```python
class Task(SQLModel, table=True):
    # ... existing fields ...

    # Recurrence fields
    is_recurring: bool = Field(
        default=False,
        description="Whether this task recurs"
    )
    recurrence_pattern: Optional[str] = Field(
        default=None,
        description="Recurrence pattern: daily, weekly, monthly"
    )
    recurrence_interval: int = Field(
        default=1,
        description="Recurrence interval (e.g., every 2 weeks)"
    )
    recurrence_end_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="When recurrence should end (optional)"
    )
    recurrence_day_of_week: Optional[int] = Field(
        default=None,
        description="Day of week for weekly recurrence (0=Monday, 6=Sunday)"
    )
    recurrence_day_of_month: Optional[int] = Field(
        default=None,
        description="Day of month for monthly recurrence (1-31)"
    )
    parent_recurrence_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id",
        description="Original recurring task template"
    )
    recurrence_active: bool = Field(
        default=True,
        description="Whether recurrence is active (can be paused)"
    )
```

### 3.2 Design Decisions

**Why add fields to tasks table instead of separate table?**
- Simpler queries (single table join)
- Recurring tasks are still tasks (share all attributes)
- Easier to maintain data consistency
- Less complex foreign key relationships

**Parent Recurrence ID**:
- Links all instances of a recurring task to the original "template"
- Enables "stop all future instances" functionality
- Allows querying all instances of a recurring task

**Recurrence Active Flag**:
- Allows pausing recurrence without deleting
- Enables "snooze" functionality
- Preserves recurrence settings for restart

## 4. Recurrence Logic

### 4.1 Recurrence Patterns

**Daily**:
- Next due date = current due date + 1 day
- Respects time of day (9am daily stays 9am)
- Simple increment

**Weekly**:
- Next due date = current due date + 7 days
- OR: next occurrence of specified day of week
- Example: "Every Monday" → next Monday from completion date
- `recurrence_day_of_week`: 0=Monday, 1=Tuesday, ..., 6=Sunday

**Monthly**:
- Next due date = same day next month
- Handle month-end: if day doesn't exist (e.g., Feb 31), use last day of month
- Example: "1st of every month" → 1st of next month
- `recurrence_day_of_month`: 1-31

### 4.2 Task Generation Rules

**When to create next instance**:
- Triggered when recurring task is marked complete
- New task created immediately upon completion
- Background job checks for missed recurrences (failsafe)

**Next instance attributes**:
```python
new_task = Task(
    user_id=completed_task.user_id,
    title=completed_task.title,
    description=completed_task.description,
    priority=completed_task.priority,
    category=completed_task.category,
    completed=False,  # New task is pending
    due_date=calculate_next_due_date(completed_task),

    # Recurrence fields copied
    is_recurring=True,
    recurrence_pattern=completed_task.recurrence_pattern,
    recurrence_interval=completed_task.recurrence_interval,
    recurrence_end_date=completed_task.recurrence_end_date,
    recurrence_day_of_week=completed_task.recurrence_day_of_week,
    recurrence_day_of_month=completed_task.recurrence_day_of_month,
    parent_recurrence_id=completed_task.parent_recurrence_id or completed_task.id,
    recurrence_active=True
)
```

**Recurrence End Conditions**:
1. `recurrence_end_date` reached → stop creating new instances
2. `recurrence_active` set to False → pause recurrence
3. User deletes recurring task → stop recurrence
4. No end condition → recurs indefinitely

### 4.3 Calculate Next Due Date Algorithm

```python
def calculate_next_due_date(task: Task) -> datetime:
    """Calculate next due date based on recurrence pattern."""

    if not task.due_date:
        # If no due date, use tomorrow as default
        base_date = datetime.now(timezone.utc) + timedelta(days=1)
    else:
        base_date = task.due_date

    if task.recurrence_pattern == "daily":
        next_date = base_date + timedelta(days=task.recurrence_interval)

    elif task.recurrence_pattern == "weekly":
        if task.recurrence_day_of_week is not None:
            # Find next occurrence of specified weekday
            days_ahead = task.recurrence_day_of_week - base_date.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_date = base_date + timedelta(days=days_ahead)
        else:
            # Simple weekly increment
            next_date = base_date + timedelta(weeks=task.recurrence_interval)

    elif task.recurrence_pattern == "monthly":
        if task.recurrence_day_of_month:
            # Next month, specific day
            next_month = base_date.month + task.recurrence_interval
            next_year = base_date.year
            while next_month > 12:
                next_month -= 12
                next_year += 1

            # Handle day overflow (e.g., Feb 31 → Feb 28/29)
            try:
                next_date = base_date.replace(
                    year=next_year,
                    month=next_month,
                    day=task.recurrence_day_of_month
                )
            except ValueError:
                # Day doesn't exist in month, use last day
                import calendar
                last_day = calendar.monthrange(next_year, next_month)[1]
                next_date = base_date.replace(
                    year=next_year,
                    month=next_month,
                    day=last_day
                )
        else:
            # Simple monthly increment
            next_date = base_date + relativedelta(months=task.recurrence_interval)

    else:
        raise ValueError(f"Unknown recurrence pattern: {task.recurrence_pattern}")

    return next_date
```

## 5. API Changes

### 5.1 MCP Tool Updates

#### 5.1.1 add_task (Enhanced)

**New Parameters**:
```python
async def execute(
    user_id: str,
    title: str,
    description: str = None,
    priority: str = "medium",
    category: str = None,
    due_date: str = None,
    # NEW RECURRENCE PARAMETERS
    is_recurring: bool = False,
    recurrence_pattern: str = None,  # 'daily', 'weekly', 'monthly'
    recurrence_interval: int = 1,
    recurrence_end_date: str = None,
    recurrence_day_of_week: int = None,  # 0-6
    recurrence_day_of_month: int = None,  # 1-31
) -> Dict[str, Any]:
```

**Validation**:
- If `is_recurring=True`, `recurrence_pattern` is required
- `recurrence_pattern` must be 'daily', 'weekly', or 'monthly'
- For weekly: `recurrence_day_of_week` recommended (0-6)
- For monthly: `recurrence_day_of_month` recommended (1-31)
- `recurrence_interval` >= 1
- `recurrence_end_date` must be in future if provided

**Example Requests**:
```json
// Daily recurring task
{
  "title": "Check email",
  "is_recurring": true,
  "recurrence_pattern": "daily",
  "due_date": "2025-12-31T09:00:00Z"
}

// Weekly recurring task (every Monday)
{
  "title": "Submit timesheet",
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_day_of_week": 0,
  "due_date": "2026-01-06T17:00:00Z"
}

// Monthly recurring task (1st of every month)
{
  "title": "Pay rent",
  "is_recurring": true,
  "recurrence_pattern": "monthly",
  "recurrence_day_of_month": 1,
  "due_date": "2026-01-01T00:00:00Z",
  "recurrence_end_date": "2026-12-31T23:59:59Z"
}
```

#### 5.1.2 complete_task (Enhanced)

**Enhanced Logic**:
```python
async def execute(user_id: str, task_id: int) -> Dict[str, Any]:
    # Mark task complete
    task.completed = True
    await session.commit()

    # If recurring, create next instance
    if task.is_recurring and task.recurrence_active:
        # Check if recurrence should end
        if task.recurrence_end_date and datetime.now(timezone.utc) >= task.recurrence_end_date:
            logger.info(f"Recurrence ended for task {task_id}")
        else:
            # Create next instance
            next_task = create_next_recurrence_instance(task)
            session.add(next_task)
            await session.commit()

            return {
                "success": True,
                "data": {...},
                "message": "Task completed. Next instance created for {next_due_date}",
                "next_task_id": next_task.id
            }

    return {"success": True, "data": {...}, "message": "Task completed"}
```

#### 5.1.3 update_task (Enhanced)

**Can Update Recurrence Settings**:
```python
async def execute(
    user_id: str,
    task_id: int,
    title: str = None,
    # ... existing parameters ...
    # NEW: Can update recurrence
    recurrence_active: bool = None,  # Pause/resume
    recurrence_end_date: str = None,  # Extend/shorten
) -> Dict[str, Any]:
```

**Use Cases**:
- Pause recurrence: `recurrence_active=False`
- Resume recurrence: `recurrence_active=True`
- Change end date: `recurrence_end_date="2026-06-30T23:59:59Z"`
- Stop recurrence: `is_recurring=False` (converts to regular task)

#### 5.1.4 list_tasks (Enhanced)

**New Filter**:
```python
async def execute(
    user_id: str,
    # ... existing parameters ...
    is_recurring: bool = None,  # Filter recurring tasks
    show_recurring_only: bool = False,  # Show only recurring templates
) -> Dict[str, Any]:
```

**Response Includes Recurrence Info**:
```json
{
  "tasks": [
    {
      "task_id": 1,
      "title": "Check email",
      "is_recurring": true,
      "recurrence_pattern": "daily",
      "recurrence_interval": 1,
      "next_due_date": "2025-12-31T09:00:00Z",
      "recurrence_active": true
    }
  ]
}
```

#### 5.1.5 New Tool: stop_recurrence

**Purpose**: Stop all future instances of a recurring task

```python
async def execute(user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Stop recurrence for a task.

    Sets recurrence_active=False to prevent future instances.
    """
    # Find task
    task = await get_task(session, user_id, task_id)

    if not task.is_recurring:
        return {
            "success": False,
            "message": "Task is not recurring"
        }

    # Stop recurrence
    task.recurrence_active = False
    await session.commit()

    return {
        "success": True,
        "message": f"Recurrence stopped for '{task.title}'. Existing task remains."
    }
```

### 5.2 REST API Endpoints (Optional)

For direct HTTP access (non-chat):

```
POST   /api/tasks/recurring              - Create recurring task
GET    /api/tasks/recurring              - List all recurring tasks
PATCH  /api/tasks/{id}/recurrence        - Update recurrence settings
DELETE /api/tasks/{id}/recurrence        - Stop recurrence
GET    /api/tasks/{id}/recurrence/instances - Get all instances of recurring task
```

## 6. Background Task Scheduler

### 6.1 Architecture Options

**Option A: Simple In-Process Scheduler** (Recommended for MVP)
- Use `APScheduler` library
- Runs background job every hour
- Checks for missed recurrences
- Simple, no external dependencies
- Works in single-instance deployment

**Option B: Celery + Redis** (Production-Ready)
- Celery for distributed task queue
- Redis as message broker
- Supports multiple workers
- Cloud-ready, scalable
- More complex setup

**Option C: Cloud-Native** (AWS/GCP)
- AWS EventBridge + Lambda
- Google Cloud Scheduler + Cloud Functions
- Fully managed, serverless
- Requires cloud provider

**Recommendation**: Start with Option A (APScheduler), migrate to Option B for production scale.

### 6.2 Scheduler Implementation (APScheduler)

**Setup**:
```python
# backend/src/scheduler/recurrence_scheduler.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)

class RecurrenceScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the recurrence check job."""
        # Run every hour
        self.scheduler.add_job(
            check_and_create_recurring_tasks,
            trigger=IntervalTrigger(hours=1),
            id="recurrence_check",
            name="Check and create recurring tasks",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Recurrence scheduler started")

    def shutdown(self):
        """Shutdown scheduler."""
        self.scheduler.shutdown()
        logger.info("Recurrence scheduler stopped")

async def check_and_create_recurring_tasks():
    """
    Background job to check for recurring tasks that need new instances.

    This is a failsafe in case completion-triggered creation fails.
    """
    logger.info("Running recurrence check...")

    async with async_session_maker() as session:
        # Find completed recurring tasks without a pending successor
        query = select(Task).where(
            Task.is_recurring == True,
            Task.recurrence_active == True,
            Task.completed == True
        )

        completed_recurring = await session.execute(query)
        tasks = completed_recurring.scalars().all()

        for task in tasks:
            # Check if next instance already exists
            next_instance_exists = await check_next_instance_exists(session, task)

            if not next_instance_exists:
                # Check if recurrence should end
                if task.recurrence_end_date and datetime.now(timezone.utc) >= task.recurrence_end_date:
                    logger.info(f"Recurrence ended for task {task.id}")
                    continue

                # Create next instance
                logger.info(f"Creating missed recurrence instance for task {task.id}")
                next_task = create_next_recurrence_instance(task)
                session.add(next_task)

        await session.commit()
        logger.info("Recurrence check complete")

async def check_next_instance_exists(session, task: Task) -> bool:
    """Check if next instance of recurring task already exists."""
    query = select(Task).where(
        Task.parent_recurrence_id == (task.parent_recurrence_id or task.id),
        Task.completed == False,
        Task.due_date > task.due_date if task.due_date else True
    ).limit(1)

    result = await session.execute(query)
    return result.scalar_one_or_none() is not None
```

**Integration with FastAPI**:
```python
# backend/src/api/app.py

from ..scheduler.recurrence_scheduler import RecurrenceScheduler

scheduler = RecurrenceScheduler()

@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup."""
    scheduler.start()
    logger.info("Application started with recurrence scheduler")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown."""
    scheduler.shutdown()
    logger.info("Application shutdown")
```

### 6.3 Cloud Deployment Considerations

**For Kubernetes/Docker**:
- Scheduler runs in each pod instance
- Use distributed locking to prevent duplicate task creation
- Use Redis for coordination

**For Serverless (Lambda/Cloud Functions)**:
- Separate scheduler service (cron trigger)
- Calls API endpoint to create tasks
- Stateless, scales automatically

**Distributed Lock Example** (using Redis):
```python
import redis
from redis.lock import Lock

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def check_and_create_recurring_tasks():
    # Acquire lock to prevent duplicate processing
    lock = redis_client.lock("recurrence_check_lock", timeout=300)

    if not lock.acquire(blocking=False):
        logger.info("Recurrence check already running, skipping")
        return

    try:
        # ... perform recurrence check ...
    finally:
        lock.release()
```

## 7. Natural Language Parsing

### 7.1 Recurrence Pattern Extraction

Update AI agent system prompt to extract recurrence patterns:

**Daily**:
- "every day", "daily", "each day"
- "remind me daily"
- "recurring task every day"

**Weekly**:
- "every week", "weekly"
- "every Monday", "every Friday"
- "each Tuesday"

**Monthly**:
- "every month", "monthly"
- "on the 1st of every month"
- "15th of each month"

**Examples**:
```
User: "Remind me to check email every day at 9am"
Extract:
  - title: "check email"
  - is_recurring: true
  - recurrence_pattern: "daily"
  - due_date: tomorrow at 09:00 (then daily)

User: "Add recurring task to submit timesheet every Monday"
Extract:
  - title: "submit timesheet"
  - is_recurring: true
  - recurrence_pattern: "weekly"
  - recurrence_day_of_week: 0 (Monday)

User: "Remind me to pay rent on the 1st of every month"
Extract:
  - title: "pay rent"
  - is_recurring: true
  - recurrence_pattern: "monthly"
  - recurrence_day_of_month: 1
```

### 7.2 AI Agent Prompt Update

Add to system prompt:
```
Recurrence Pattern Extraction:
- "every day", "daily" → recurrence_pattern="daily"
- "every week", "weekly" → recurrence_pattern="weekly"
- "every month", "monthly" → recurrence_pattern="monthly"
- "every Monday" → recurrence_pattern="weekly", recurrence_day_of_week=0
- "every Tuesday" → recurrence_pattern="weekly", recurrence_day_of_week=1
- "on the 1st" → recurrence_day_of_month=1
- "on the 15th" → recurrence_day_of_month=15

When user says "stop recurring" or "cancel recurrence":
  - Use stop_recurrence tool
```

## 8. Frontend Integration

### 8.1 UI Components Needed

#### 8.1.1 Recurring Task Badge

Display recurring indicator on task cards:

```tsx
{task.is_recurring && (
  <span className="recurring-badge">
    <span className="icon">🔄</span>
    <span className="pattern">{formatRecurrencePattern(task)}</span>
  </span>
)}

function formatRecurrencePattern(task) {
  if (task.recurrence_pattern === 'daily') return 'Daily';
  if (task.recurrence_pattern === 'weekly') {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return `Weekly${task.recurrence_day_of_week !== null ? ` (${days[task.recurrence_day_of_week]})` : ''}`;
  }
  if (task.recurrence_pattern === 'monthly') {
    return `Monthly${task.recurrence_day_of_month ? ` (${task.recurrence_day_of_month}${getDaySuffix(task.recurrence_day_of_month)})` : ''}`;
  }
  return 'Recurring';
}
```

#### 8.1.2 Recurrence Form Fields (Optional Direct UI)

```tsx
<div className="recurrence-section">
  <label>
    <input
      type="checkbox"
      checked={isRecurring}
      onChange={(e) => setIsRecurring(e.target.checked)}
    />
    Make this a recurring task
  </label>

  {isRecurring && (
    <>
      <select value={recurrencePattern} onChange={(e) => setRecurrencePattern(e.target.value)}>
        <option value="daily">Daily</option>
        <option value="weekly">Weekly</option>
        <option value="monthly">Monthly</option>
      </select>

      {recurrencePattern === 'weekly' && (
        <select value={dayOfWeek} onChange={(e) => setDayOfWeek(e.target.value)}>
          <option value="0">Monday</option>
          <option value="1">Tuesday</option>
          <option value="2">Wednesday</option>
          <option value="3">Thursday</option>
          <option value="4">Friday</option>
          <option value="5">Saturday</option>
          <option value="6">Sunday</option>
        </select>
      )}

      {recurrencePattern === 'monthly' && (
        <input
          type="number"
          min="1"
          max="31"
          value={dayOfMonth}
          onChange={(e) => setDayOfMonth(e.target.value)}
          placeholder="Day of month (1-31)"
        />
      )}

      <input
        type="date"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
        placeholder="End date (optional)"
      />
    </>
  )}
</div>
```

#### 8.1.3 Stop Recurrence Button

```tsx
{task.is_recurring && task.recurrence_active && (
  <button
    onClick={() => handleStopRecurrence(task.id)}
    className="btn-stop-recurrence"
  >
    Stop Recurrence
  </button>
)}

async function handleStopRecurrence(taskId) {
  const response = await apiClient.stopRecurrence(taskId);
  if (response.success) {
    alert('Recurrence stopped. Task will not repeat.');
    refreshTasks();
  }
}
```

### 8.2 Chat Interface (Primary Method)

Users can manage recurring tasks via natural language:

```
User: "Add recurring task to check email every day at 9am"
AI: ✅ Created recurring task 'check email' (Task #10)
    Recurrence: Daily at 9:00 AM
    Next due: Tomorrow at 9:00 AM

User: "Show my recurring tasks"
AI: 📋 You have 3 recurring tasks:
    1. Check email - Daily at 9:00 AM
    2. Submit timesheet - Every Monday at 5:00 PM
    3. Pay rent - Monthly on the 1st

User: "Stop the email reminder"
AI: ✅ Stopped recurrence for 'check email'
    The current task remains, but won't repeat.
```

## 9. Testing Scenarios

### 9.1 Unit Tests

**Test Daily Recurrence**:
```python
def test_daily_recurrence():
    task = create_task(is_recurring=True, recurrence_pattern='daily', due_date='2025-12-30T09:00:00Z')
    next_date = calculate_next_due_date(task)
    assert next_date == datetime(2025, 12, 31, 9, 0, 0, tzinfo=timezone.utc)
```

**Test Weekly Recurrence**:
```python
def test_weekly_recurrence_monday():
    task = create_task(
        is_recurring=True,
        recurrence_pattern='weekly',
        recurrence_day_of_week=0,  # Monday
        due_date='2025-12-30T17:00:00Z'  # Tuesday
    )
    next_date = calculate_next_due_date(task)
    # Should be next Monday
    assert next_date.weekday() == 0
```

**Test Monthly Recurrence**:
```python
def test_monthly_recurrence_first():
    task = create_task(
        is_recurring=True,
        recurrence_pattern='monthly',
        recurrence_day_of_month=1,
        due_date='2025-12-01T00:00:00Z'
    )
    next_date = calculate_next_due_date(task)
    assert next_date == datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
```

**Test Month-End Handling**:
```python
def test_monthly_recurrence_month_end():
    task = create_task(
        is_recurring=True,
        recurrence_pattern='monthly',
        recurrence_day_of_month=31,
        due_date='2025-01-31T00:00:00Z'
    )
    next_date = calculate_next_due_date(task)
    # February doesn't have 31 days, should be Feb 28 (or 29 in leap year)
    assert next_date.day in [28, 29]
    assert next_date.month == 2
```

### 9.2 Integration Tests

**Test Task Completion Creates Next Instance**:
```python
async def test_complete_recurring_task_creates_next():
    # Create recurring task
    task = await add_task(user_id="test", title="Email", is_recurring=True, recurrence_pattern="daily")

    # Complete it
    result = await complete_task(user_id="test", task_id=task.id)

    # Check next instance was created
    assert result['next_task_id'] is not None
    next_task = await get_task(result['next_task_id'])
    assert next_task.completed == False
    assert next_task.parent_recurrence_id == task.id
```

**Test Recurrence End Date**:
```python
async def test_recurrence_respects_end_date():
    end_date = datetime.now(timezone.utc) - timedelta(days=1)  # Yesterday
    task = await add_task(
        user_id="test",
        title="Test",
        is_recurring=True,
        recurrence_pattern="daily",
        recurrence_end_date=end_date.isoformat()
    )

    # Complete task
    result = await complete_task(user_id="test", task_id=task.id)

    # Should NOT create next instance (end date passed)
    assert 'next_task_id' not in result
```

### 9.3 Natural Language Tests

**Test Chat Interface**:
```
Input: "Add recurring task to check email every day"
Expected: Creates task with is_recurring=True, recurrence_pattern="daily"

Input: "Remind me every Monday to submit timesheet"
Expected: Creates task with recurrence_pattern="weekly", recurrence_day_of_week=0

Input: "Stop the daily email reminder"
Expected: Finds task, calls stop_recurrence
```

## 10. Security & Performance

### 10.1 Security Considerations

- **User Isolation**: Recurring tasks respect user_id boundaries
- **Rate Limiting**: Prevent creating excessive recurring tasks
- **Validation**: Strict validation on recurrence parameters
- **Permissions**: Only task owner can stop/modify recurrence

### 10.2 Performance Optimizations

- **Indexes**: Added indexes on is_recurring, recurrence_active, parent_recurrence_id
- **Batch Processing**: Scheduler processes tasks in batches
- **Lazy Loading**: Only load recurrence fields when needed
- **Caching**: Cache recurring task templates

### 10.3 Scalability

- **Horizontal Scaling**: Use distributed lock for scheduler
- **Database**: PostgreSQL handles concurrent task creation
- **Background Jobs**: APScheduler → Celery for distributed processing
- **Cloud-Ready**: Scheduler can run as separate service

## 11. Rollout Strategy

### Phase 1: Core Functionality (Week 1)
- Database migration
- Add recurrence fields to Task model
- Update add_task, complete_task tools
- Basic recurrence logic (daily, weekly, monthly)

### Phase 2: Scheduler (Week 1-2)
- Implement APScheduler
- Background job for missed recurrences
- Testing and monitoring

### Phase 3: AI Agent (Week 2)
- Update system prompt
- Natural language extraction
- Testing with sample queries

### Phase 4: Frontend (Week 2-3)
- Recurring task badges
- Chat interface testing
- Optional: Direct UI forms

### Phase 5: Production (Week 3+)
- Load testing
- Monitoring and alerting
- Migrate to Celery if needed
- Deploy to production

## 12. Success Metrics

- ✅ Users can create daily/weekly/monthly recurring tasks
- ✅ 95%+ of recurring tasks generate next instance on completion
- ✅ Scheduler detects and creates missed recurrences within 1 hour
- ✅ Natural language parsing accuracy >90% for recurrence patterns
- ✅ No duplicate task creation (idempotency)
- ✅ Background jobs complete within 5 minutes
- ✅ System scales to 10,000+ recurring tasks per user

## 13. Open Questions

1. **Should we support "every 2 weeks" (bi-weekly)?**
   - Yes, via `recurrence_interval=2` with pattern="weekly"

2. **How to handle timezone for recurring tasks?**
   - Store all dates in UTC, calculate next due date in UTC
   - Frontend displays in user's local timezone

3. **Can users modify past instances of recurring tasks?**
   - No, only future instances can be affected by stopping recurrence

4. **What happens if user completes future instance early?**
   - Creates next instance as normal (based on original due date)

5. **Should we notify users of created recurring tasks?**
   - Future enhancement: email/push notifications

---

**Next Steps**:
1. Review and approve this specification
2. Create implementation plan (`plan.md`)
3. Generate task breakdown (`tasks.md`)
4. Begin implementation
