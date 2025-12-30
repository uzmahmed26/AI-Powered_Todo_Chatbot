# Recurring Tasks Implementation Status

## ✅ Completed (Phase 1 - Foundation)

### 1. Database Migration
- **File**: `backend/alembic/versions/004_add_recurring_tasks.py`
- **Status**: ✅ Created
- **Contents**: Adds 8 new fields, 3 indexes, 1 foreign key

### 2. Task Model Updates
- **File**: `backend/src/models/task.py`
- **Status**: ✅ Updated
- **Changes**: Added 8 recurrence fields to Task model

### 3. Recurrence Logic Utilities
- **File**: `backend/src/utils/recurrence.py`
- **Status**: ✅ Created
- **Functions**:
  - `calculate_next_due_date()` - Main recurrence calculation
  - `_calculate_daily_recurrence()` - Daily pattern logic
  - `_calculate_weekly_recurrence()` - Weekly pattern logic
  - `_calculate_monthly_recurrence()` - Monthly pattern logic (handles month-end overflow)
  - `should_create_next_instance()` - Check if recurrence should continue
  - `create_next_recurrence_instance()` - Build data for next task

## 🔄 In Progress

### 4. MCP Schemas Updates
- **File**: `backend/src/mcp_server/schemas.py`
- **Status**: Needs completion
- **Required Changes**:
  - Add recurrence fields to `AddTaskInput`
  - Add recurrence fields to `UpdateTaskInput`
  - Add recurrence filters to `ListTasksInput`
  - Update `TaskData` to include recurrence fields
  - Add validators for recurrence_pattern, day_of_week, day_of_month

## ⏳ Remaining Work

### Phase 2: MCP Tools (Priority: HIGH)

#### 5. Update add_task Tool
- **File**: `backend/src/mcp_server/tools/add_task.py`
- **Changes Needed**:
  - Add 6 new parameters (is_recurring, recurrence_pattern, etc.)
  - Add validation for recurrence parameters
  - Include recurrence fields in response

#### 6. Update complete_task Tool
- **File**: `backend/src/mcp_server/tools/complete_task.py`
- **Changes Needed**:
  - Import recurrence utilities
  - After marking complete, check if recurring
  - If recurring and active, create next instance using `create_next_recurrence_instance()`
  - Return next_task_id in response

#### 7. Create stop_recurrence Tool
- **File**: `backend/src/mcp_server/tools/stop_recurrence.py` (NEW)
- **Functionality**:
  - Accept user_id and task_id
  - Find task, verify it's recurring
  - Set recurrence_active = False
  - Return success message

#### 8. Update list_tasks Tool
- **File**: `backend/src/mcp_server/tools/list_tasks.py`
- **Changes Needed**:
  - Add is_recurring filter parameter
  - Include recurrence fields in task_list response

#### 9. Update update_task Tool
- **File**: `backend/src/mcp_server/tools/update_task.py`
- **Changes Needed**:
  - Add recurrence_active parameter (pause/resume)
  - Add recurrence_end_date parameter

### Phase 3: MCP Server & Agent (Priority: HIGH)

#### 10. Update MCP Server Tool Definitions
- **File**: `backend/src/mcp_server/server.py`
- **Changes Needed**:
  - Update add_task schema with recurrence parameters
  - Register stop_recurrence tool
  - Update list_tasks schema

#### 11. Update AI Agent System Prompt
- **File**: `backend/src/agent/agent.py`
- **Changes Needed**:
  - Add recurrence pattern extraction rules
  - Add examples for "every day", "every Monday", "1st of month"
  - Add stop_recurrence tool description

### Phase 4: Background Scheduler (Priority: MEDIUM)

#### 12. Install APScheduler
```bash
cd backend
pip install apscheduler python-dateutil
pip freeze > requirements.txt
```

#### 13. Create Scheduler Module
- **File**: `backend/src/scheduler/recurrence_scheduler.py` (NEW)
- **Functionality**:
  - AsyncIOScheduler setup
  - Hourly job to check for missed recurrences
  - Find completed recurring tasks without next instance
  - Create missed instances

#### 14. Integrate Scheduler with FastAPI
- **File**: `backend/src/api/app.py`
- **Changes Needed**:
  - Import RecurrenceScheduler
  - Start scheduler on app startup
  - Stop scheduler on app shutdown

### Phase 5: Testing & Deployment (Priority: MEDIUM)

#### 15. Run Migration
```bash
cd backend
python -m alembic upgrade head
```

#### 16. Test Scenarios
- Create daily recurring task via chat
- Create weekly recurring task (specific day)
- Create monthly recurring task (specific date)
- Complete recurring task → verify next instance created
- Stop recurrence
- Test month-end overflow (31st → last day of month)

#### 17. Commit & Deploy
```bash
git add .
git commit -m "feat(tasks): add recurring tasks with daily/weekly/monthly patterns"
git push
```

## Quick Implementation Guide

### Minimal Viable Implementation (MVP)

To get recurring tasks working quickly, implement in this order:

1. **Run Migration** (5 min)
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

2. **Update Schemas** (15 min)
   - Add recurrence fields to AddTaskInput
   - Add validators

3. **Update add_task** (15 min)
   - Add recurrence parameters
   - Save to database

4. **Update complete_task** (20 min)
   - Import recurrence utils
   - Check if recurring
   - Create next instance

5. **Create stop_recurrence** (10 min)
   - New tool file
   - Set recurrence_active=False

6. **Update Agent Prompt** (10 min)
   - Add recurrence extraction examples

7. **Test** (15 min)
   - "Add task every day to check email"
   - Complete it
   - Verify next instance created

**Total MVP Time**: ~90 minutes

### Full Implementation (with Scheduler)

Add scheduler after MVP works:

8. **Install Dependencies** (5 min)
9. **Create Scheduler** (30 min)
10. **Integrate with FastAPI** (10 min)
11. **Test Scheduler** (15 min)

**Total Time**: ~2.5 hours

## Current Files

### Created ✅
1. `backend/alembic/versions/004_add_recurring_tasks.py`
2. `backend/src/utils/recurrence.py`
3. `specs/009-recurring-tasks/spec.md`
4. `specs/009-recurring-tasks/QUICK_REFERENCE.md`
5. `specs/009-recurring-tasks/README.md`
6. `specs/009-recurring-tasks/IMPLEMENTATION_STATUS.md` (this file)

### Modified ✅
1. `backend/src/models/task.py` - Added 8 recurrence fields

### To Create 🔄
1. `backend/src/mcp_server/tools/stop_recurrence.py`
2. `backend/src/scheduler/__init__.py`
3. `backend/src/scheduler/recurrence_scheduler.py`

### To Modify 🔄
1. `backend/src/mcp_server/schemas.py`
2. `backend/src/mcp_server/tools/add_task.py`
3. `backend/src/mcp_server/tools/complete_task.py`
4. `backend/src/mcp_server/tools/update_task.py`
5. `backend/src/mcp_server/tools/list_tasks.py`
6. `backend/src/mcp_server/server.py`
7. `backend/src/agent/agent.py`
8. `backend/src/api/app.py`
9. `backend/requirements.txt`

## Next Steps

1. **Run the migration** to add database fields
2. **Follow MVP implementation guide** (90 minutes)
3. **Test basic recurrence** (daily pattern)
4. **Add scheduler** for production-readiness
5. **Deploy and monitor**

## Code Snippets for Quick Implementation

### Add to AddTaskInput in schemas.py

```python
# Recurrence fields
is_recurring: bool = Field(default=False)
recurrence_pattern: Optional[str] = Field(None, description="daily, weekly, monthly")
recurrence_interval: int = Field(default=1, ge=1)
recurrence_end_date: Optional[str] = Field(None)
recurrence_day_of_week: Optional[int] = Field(None, ge=0, le=6)
recurrence_day_of_month: Optional[int] = Field(None, ge=1, le=31)

@field_validator("recurrence_pattern")
@classmethod
def validate_recurrence_pattern(cls, v):
    if v is not None and v not in ["daily", "weekly", "monthly"]:
        raise ValueError("recurrence_pattern must be daily, weekly, or monthly")
    return v
```

### Add to add_task.py execute function

```python
# At top of file
from ...utils.recurrence import calculate_next_due_date

# In function signature
is_recurring: bool = False,
recurrence_pattern: str = None,
recurrence_interval: int = 1,
recurrence_end_date: str = None,
recurrence_day_of_week: int = None,
recurrence_day_of_month: int = None,

# When creating task
new_task = Task(
    # ... existing fields ...
    is_recurring=is_recurring,
    recurrence_pattern=recurrence_pattern,
    recurrence_interval=recurrence_interval,
    recurrence_end_date=parsed_end_date,
    recurrence_day_of_week=recurrence_day_of_week,
    recurrence_day_of_month=recurrence_day_of_month,
    recurrence_active=True
)
```

### Add to complete_task.py

```python
# After marking task complete
if task.is_recurring and task.recurrence_active:
    from ...utils.recurrence import should_create_next_instance, create_next_recurrence_instance

    if should_create_next_instance(task.recurrence_end_date, task.recurrence_active):
        next_task_data = create_next_recurrence_instance(task)
        next_task = Task(**next_task_data)
        session.add(next_task)
        await session.commit()
        await session.refresh(next_task)

        return {
            "success": True,
            "message": f"Task completed. Next instance created for {next_task.due_date}",
            "next_task_id": next_task.id
        }
```

---

**Status**: Phase 1 Complete (Foundation)
**Next**: Phase 2 (MCP Tools) - Est. 90 minutes for MVP
**Total Progress**: ~30% complete
