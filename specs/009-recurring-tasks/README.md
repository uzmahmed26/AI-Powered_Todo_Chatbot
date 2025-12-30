# Feature 009: Recurring Tasks

## Overview

Add recurring tasks functionality to enable users to create tasks that automatically regenerate on a schedule (daily, weekly, monthly). When a recurring task is completed, the system automatically creates the next instance with the same attributes.

## Documentation

This feature includes comprehensive documentation:

### 1. [spec.md](./spec.md) - Complete Feature Specification
- **Purpose**: Full requirements and design document
- **Audience**: Product managers, architects, developers
- **Contents**:
  - User stories with acceptance criteria
  - Database schema changes (8 new fields)
  - Recurrence logic and algorithms
  - API endpoint specifications
  - Background scheduler design
  - Natural language parsing rules
  - Testing scenarios
  - Security and scalability considerations

### 2. [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick Reference Guide
- **Purpose**: Fast lookup for developers during implementation
- **Audience**: Developers (during coding)
- **Contents**:
  - Database schema summary
  - API changes at a glance
  - Recurrence pattern examples
  - Natural language extraction examples
  - Frontend code snippets
  - Testing checklist
  - Troubleshooting guide

## Quick Start

### For Reviewers
1. Start with `spec.md` section 1-2 for overview and user stories
2. Review recurrence logic in section 4
3. Check background scheduler design in section 6

### For Implementers
1. Read `spec.md` for full context
2. Use `QUICK_REFERENCE.md` during implementation
3. Follow phased rollout strategy in section 11

### For Testers
1. Review testing scenarios in `spec.md` section 9
2. Use testing checklist in `QUICK_REFERENCE.md`
3. Test natural language extraction

## Key Features

- ✅ **Daily Recurrence**: Tasks repeat every day (e.g., "check email daily")
- ✅ **Weekly Recurrence**: Tasks repeat on specific weekday (e.g., "every Monday")
- ✅ **Monthly Recurrence**: Tasks repeat on specific day of month (e.g., "1st of every month")
- ✅ **Auto-Generation**: Next task created automatically on completion
- ✅ **Attribute Preservation**: Priority, category, description carried forward
- ✅ **End Dates**: Optional end date for finite recurrence
- ✅ **Pause/Resume**: Stop and restart recurrence without deleting
- ✅ **Natural Language**: Parse recurrence from conversational input
- ✅ **Background Scheduler**: Failsafe to catch missed recurrences
- ✅ **Cloud-Ready**: Scalable with distributed locking

## Implementation Status

- [ ] Database migration created
- [ ] Task model updated with recurrence fields
- [ ] Recurrence logic implemented
- [ ] MCP tools updated (add_task, complete_task, update_task)
- [ ] New tool: stop_recurrence
- [ ] Background scheduler (APScheduler)
- [ ] AI agent prompt updated
- [ ] Frontend recurring badge
- [ ] Testing complete

## Technical Stack

- **Backend**: FastAPI, Python 3.11+, SQLModel, PostgreSQL
- **Scheduler**: APScheduler (MVP) → Celery + Redis (Production)
- **Frontend**: React 18, TypeScript, Vite
- **AI Agent**: OpenAI GPT-4 with MCP tools
- **Database**: PostgreSQL 14+

## Database Changes

### New Fields (8 total)

| Field | Type | Description |
|-------|------|-------------|
| `is_recurring` | BOOLEAN | Whether task recurs |
| `recurrence_pattern` | VARCHAR(20) | daily/weekly/monthly |
| `recurrence_interval` | INTEGER | Frequency (e.g., every 2 weeks) |
| `recurrence_end_date` | TIMESTAMP | Optional end date |
| `recurrence_day_of_week` | INTEGER | 0-6 for weekly |
| `recurrence_day_of_month` | INTEGER | 1-31 for monthly |
| `parent_recurrence_id` | INTEGER | Links to original task |
| `recurrence_active` | BOOLEAN | Can pause recurrence |

### Indexes (3 new)

- `idx_task_is_recurring`
- `idx_task_recurrence_active`
- `idx_task_parent_recurrence`

## Natural Language Examples

### Creating Recurring Tasks

```
User: "Remind me to check email every day at 9am"
AI: ✅ Created recurring task 'check email' (Task #10)
    Recurrence: Daily at 9:00 AM
    Next due: Tomorrow at 9:00 AM

User: "Add recurring task to submit timesheet every Monday"
AI: ✅ Created recurring task 'submit timesheet' (Task #15)
    Recurrence: Every Monday
    Next due: Jan 6, 2026 at 12:00 PM

User: "Pay rent on the 1st of every month"
AI: ✅ Created recurring task 'pay rent' (Task #20)
    Recurrence: Monthly on the 1st
    Next due: Jan 1, 2026
```

### Managing Recurring Tasks

```
User: "Show my recurring tasks"
AI: 📋 You have 3 recurring tasks:
    1. Check email - Daily at 9:00 AM
    2. Submit timesheet - Every Monday
    3. Pay rent - Monthly on the 1st

User: "Stop the daily email reminder"
AI: ✅ Stopped recurrence for 'check email'
    The current task remains, but won't repeat.
```

## Architecture Highlights

### Recurrence Generation

**Trigger**: Task completion
- When user completes recurring task, next instance created immediately
- Preserves all attributes (title, priority, category, etc.)
- Calculates next due date based on pattern

**Failsafe**: Background scheduler
- Runs hourly to check for missed recurrences
- Creates instances if completion trigger failed
- Prevents data loss from system errors

### Scalability

**Single Instance** (MVP):
- APScheduler in-process
- Simple, no external dependencies
- Works for 1-10,000 users

**Multi-Instance** (Production):
- Celery + Redis for distributed task queue
- Distributed locking prevents duplicates
- Horizontal scaling support

**Cloud-Native** (Future):
- AWS EventBridge + Lambda
- Google Cloud Scheduler + Functions
- Fully managed, serverless

## Recurrence Patterns

### Daily
```python
# Every day at same time
next_date = current_date + timedelta(days=1)

# Every 2 days
next_date = current_date + timedelta(days=2)
```

### Weekly
```python
# Every Monday
next_monday = current_date + timedelta(days=(0 - current_date.weekday()) % 7)

# Every Friday
next_friday = current_date + timedelta(days=(4 - current_date.weekday()) % 7)
```

### Monthly
```python
# 1st of every month
next_date = datetime(year, month + 1, 1)

# 31st with overflow handling
try:
    next_date = datetime(year, month + 1, 31)
except ValueError:
    # Use last day of month
    next_date = datetime(year, month + 1, last_day_of_month)
```

## API Examples

### Create Daily Recurring Task

```json
POST /api/{user_id}/chat
{
  "message": "Add recurring task to check email every day at 9am"
}

// AI extracts and calls add_task with:
{
  "title": "check email",
  "is_recurring": true,
  "recurrence_pattern": "daily",
  "due_date": "2025-12-31T09:00:00Z"
}
```

### Create Weekly Recurring Task

```json
{
  "message": "Remind me every Monday to submit timesheet"
}

// Calls add_task with:
{
  "title": "submit timesheet",
  "is_recurring": true,
  "recurrence_pattern": "weekly",
  "recurrence_day_of_week": 0,  // Monday
  "due_date": "2026-01-06T17:00:00Z"
}
```

### Create Monthly Recurring Task

```json
{
  "message": "Pay rent on the 1st of every month"
}

// Calls add_task with:
{
  "title": "pay rent",
  "is_recurring": true,
  "recurrence_pattern": "monthly",
  "recurrence_day_of_month": 1,
  "due_date": "2026-01-01T00:00:00Z"
}
```

### Stop Recurrence

```json
{
  "message": "Stop the daily email reminder"
}

// Calls stop_recurrence(task_id)
// Response: "Recurrence stopped. Current task remains."
```

## Dependencies

### Backend

**New**:
- `apscheduler>=3.10.0` - Background task scheduler
- `python-dateutil>=2.8.2` - Advanced date calculations

**Existing**:
- FastAPI, SQLModel, PostgreSQL, OpenAI (already installed)

### Frontend

**No new dependencies** - Uses existing React stack

## Success Metrics

- ✅ Users can create daily/weekly/monthly recurring tasks
- ✅ 95%+ of recurring tasks auto-generate next instance on completion
- ✅ Scheduler detects missed recurrences within 1 hour
- ✅ Natural language accuracy >90% for recurrence patterns
- ✅ Zero duplicate task creation (idempotency guaranteed)
- ✅ Background jobs complete within 5 minutes
- ✅ System scales to 10,000+ recurring tasks per user

## Edge Cases Handled

1. **Month-End Overflow**: Feb 31 → Feb 28/29
2. **Timezone**: All dates in UTC, displayed in user local time
3. **Missed Recurrences**: Scheduler catches and creates
4. **Duplicate Prevention**: Distributed locking in multi-instance
5. **Completion Before Due**: Creates next from original schedule
6. **End Date Reached**: Stops creating new instances
7. **Paused Recurrence**: Preserves settings for restart

## Rollout Strategy

### Phase 1: Core (Week 1)
- Database migration
- Recurrence fields in Task model
- Basic logic (daily, weekly, monthly)

### Phase 2: Scheduler (Week 1-2)
- APScheduler setup
- Background job implementation
- Testing and monitoring

### Phase 3: AI Agent (Week 2)
- System prompt updates
- Natural language extraction
- Chat interface testing

### Phase 4: Frontend (Week 2-3)
- Recurring badges
- Stop recurrence button
- Optional: Direct UI forms

### Phase 5: Production (Week 3+)
- Load testing
- Distributed locking (Redis)
- Migrate to Celery if needed
- Deploy with monitoring

## Future Enhancements (Out of Scope)

- Complex patterns ("every other Tuesday", "last Friday of month")
- Multiple recurrence rules per task
- Recurrence exceptions (skip Christmas, etc.)
- Task series view (all instances)
- Sync with Google Calendar / Outlook
- Recurring task templates
- Bulk operations on recurring tasks

## Next Steps

1. **Review**: Review and approve the specification
2. **Plan**: Create detailed implementation plan if needed
3. **Implement**: Follow phased rollout strategy
4. **Test**: Run all test scenarios
5. **Deploy**: Start with Phase 1, iterate to Phase 5

## Questions or Issues?

- For specification questions, see `spec.md`
- For quick lookups, see `QUICK_REFERENCE.md`
- For implementation planning, create `IMPLEMENTATION_GUIDE.md`
- For general questions, ask the AI assistant

---

**Feature ID**: 009-recurring-tasks
**Status**: Planning Complete
**Created**: 2025-12-30
**Priority**: High
**Dependencies**: 008-todo-upgrade
**Estimated Effort**: 2-3 weeks
