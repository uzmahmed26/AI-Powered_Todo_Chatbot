# Agent Skills - Quick Reference

## Skill Catalog

| Skill | Input | Output | Use Case |
|-------|-------|--------|----------|
| `extract_tasks` | Text | List[Task] | Parse multiple tasks from text |
| `prioritize_task` | Task | Priority + Reasoning | Auto-assign priority level |
| `suggest_schedule` | Task | Due Date + Time | Suggest optimal scheduling |
| `classify_category` | Task | Category | Auto-categorize tasks |
| `breakdown_task` | Task | List[Subtask] | Split complex tasks |

---

## API Reference

### Base URL
```
https://your-domain.com/api/{user_id}/skills
```

### Authentication
All endpoints require JWT token in `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

---

## 1. Extract Tasks

### Endpoint
```http
POST /api/{user_id}/skills/extract_tasks
```

### Request
```json
{
  "input": {
    "text": "Buy milk, call John, and prepare presentation",
    "max_tasks": 10
  }
}
```

### Response
```json
{
  "success": true,
  "skill": "extract_tasks",
  "output": {
    "tasks": [
      {"title": "Buy milk", "description": null, "confidence": 0.95},
      {"title": "Call John", "description": null, "confidence": 0.90},
      {"title": "Prepare presentation", "description": null, "confidence": 0.92}
    ],
    "count": 3
  },
  "execution_time_ms": 523
}
```

### Input Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | Text to extract tasks from |
| context | string | No | Additional context |
| max_tasks | int | No | Max tasks to extract (default: 10) |

### Output Schema
| Field | Type | Description |
|-------|------|-------------|
| tasks | array | List of extracted tasks |
| tasks[].title | string | Task title |
| tasks[].description | string? | Task description |
| tasks[].confidence | float | Confidence score (0-1) |
| count | int | Total tasks extracted |

---

## 2. Prioritize Task

### Endpoint
```http
POST /api/{user_id}/skills/prioritize_task
```

### Request
```json
{
  "input": {
    "title": "Fix production bug",
    "description": "Critical issue affecting users",
    "due_date": "2025-01-02T23:59:59Z",
    "category": "work"
  }
}
```

### Response
```json
{
  "success": true,
  "skill": "prioritize_task",
  "output": {
    "priority": "high",
    "reasoning": "Critical issue with upcoming deadline in work category",
    "confidence": 0.95
  },
  "execution_time_ms": 234
}
```

### Input Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |
| due_date | datetime | No | Due date (ISO 8601) |
| category | string | No | Task category |
| context | string | No | User's workload context |

### Output Schema
| Field | Type | Description |
|-------|------|-------------|
| priority | enum | "high", "medium", or "low" |
| reasoning | string | Explanation of priority |
| confidence | float | Confidence score (0-1) |

### Priority Rules
- **High**: Keywords (urgent, critical, ASAP) OR due < 24h OR work + deadline
- **Medium**: Due 1-3 days OR important keywords
- **Low**: Due > 7 days OR no deadline + personal category

---

## 3. Suggest Schedule

### Endpoint
```http
POST /api/{user_id}/skills/suggest_schedule
```

### Request
```json
{
  "input": {
    "title": "Team standup meeting",
    "description": "Daily sync with team",
    "priority": "high",
    "category": "work",
    "relative_date": "tomorrow"
  }
}
```

### Response
```json
{
  "success": true,
  "skill": "suggest_schedule",
  "output": {
    "suggested_due_date": "2025-01-02T09:00:00Z",
    "reasoning": "Work meetings typically scheduled in morning hours",
    "time_of_day": "morning",
    "confidence": 0.88
  },
  "execution_time_ms": 198
}
```

### Input Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |
| priority | string | No | Task priority |
| category | string | No | Task category |
| relative_date | string | No | "tomorrow", "next week", etc. |

### Output Schema
| Field | Type | Description |
|-------|------|-------------|
| suggested_due_date | datetime | Suggested due date/time (ISO 8601) |
| reasoning | string | Explanation of suggestion |
| time_of_day | enum | "morning", "afternoon", "evening", "specific" |
| confidence | float | Confidence score (0-1) |

### Time-of-Day Heuristics
- **Morning** (9 AM): standup, meeting, email
- **Afternoon** (2 PM): work, project tasks
- **Evening** (6 PM): review, planning, personal tasks
- **Specific Time**: appointments, calls

---

## 4. Classify Category

### Endpoint
```http
POST /api/{user_id}/skills/classify_category
```

### Request
```json
{
  "input": {
    "title": "Buy groceries for dinner",
    "description": "Get milk, bread, eggs"
  }
}
```

### Response
```json
{
  "success": true,
  "skill": "classify_category",
  "output": {
    "category": "shopping",
    "confidence": 0.92,
    "reasoning": "Contains shopping keywords: 'buy', 'groceries'"
  },
  "execution_time_ms": 156
}
```

### Input Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |

### Output Schema
| Field | Type | Description |
|-------|------|-------------|
| category | enum | work, home, study, personal, shopping, health, fitness |
| confidence | float | Confidence score (0-1) |
| reasoning | string | Explanation of classification |

### Category Keywords
- **Work**: meeting, report, project, deadline, presentation
- **Shopping**: buy, purchase, groceries, order
- **Health**: doctor, appointment, medication, checkup
- **Fitness**: gym, workout, exercise, run
- **Study**: study, homework, assignment, exam
- **Home**: clean, fix, repair, organize

---

## 5. Break Down Task

### Endpoint
```http
POST /api/{user_id}/skills/breakdown_task
```

### Request
```json
{
  "input": {
    "title": "Deploy new feature to production",
    "description": "Deploy user authentication feature",
    "max_subtasks": 5
  }
}
```

### Response
```json
{
  "success": true,
  "skill": "breakdown_task",
  "output": {
    "subtasks": [
      {"title": "Run all tests", "order": 1, "estimated_duration": "30m"},
      {"title": "Create pull request", "order": 2, "estimated_duration": "15m"},
      {"title": "Get code review approval", "order": 3, "estimated_duration": "2h"},
      {"title": "Merge to main branch", "order": 4, "estimated_duration": "5m"},
      {"title": "Deploy to production", "order": 5, "estimated_duration": "30m"}
    ],
    "total_estimated_duration": "3h20m"
  },
  "execution_time_ms": 892
}
```

### Input Schema
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Task title |
| description | string | No | Task description |
| max_subtasks | int | No | Max subtasks to generate (default: 5) |

### Output Schema
| Field | Type | Description |
|-------|------|-------------|
| subtasks | array | List of subtasks |
| subtasks[].title | string | Subtask title |
| subtasks[].description | string? | Subtask description |
| subtasks[].order | int | Sequence number (1-based) |
| subtasks[].estimated_duration | string? | Estimated time (e.g., "30m", "2h") |
| total_estimated_duration | string? | Total estimated time |

---

## Skill Chaining

Execute multiple skills in sequence, passing output to next input.

### Endpoint
```http
POST /api/{user_id}/skills/chain
```

### Request
```json
{
  "skills": ["extract_tasks", "prioritize_task", "classify_category"],
  "input": {
    "text": "Urgent: finish Q4 report by Friday"
  }
}
```

### Response
```json
{
  "success": true,
  "chain": ["extract_tasks", "prioritize_task", "classify_category"],
  "output": {
    "title": "Finish Q4 report",
    "priority": "high",
    "category": "work",
    "reasoning": "Urgent keyword detected, work-related content"
  },
  "execution_time_ms": 1247
}
```

---

## Batch Operations

Apply a skill to multiple existing tasks at once.

### Endpoint
```http
POST /api/{user_id}/skills/{skill_name}/batch
```

### Request
```json
{
  "task_ids": [1, 2, 3, 4, 5]
}
```

### Response
```json
{
  "success": true,
  "skill": "prioritize_task",
  "results": [
    {"task_id": 1, "priority": "high", "updated": true},
    {"task_id": 2, "priority": "medium", "updated": true},
    {"task_id": 3, "priority": "low", "updated": true},
    {"task_id": 4, "priority": "high", "updated": true},
    {"task_id": 5, "priority": "medium", "updated": true}
  ],
  "total_processed": 5,
  "total_updated": 5,
  "execution_time_ms": 2341
}
```

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input: 'text' field is required",
    "details": {
      "field": "text",
      "constraint": "required"
    }
  }
}
```

### Error Codes
| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `SKILL_NOT_FOUND` | Skill name not registered |
| `EXECUTION_ERROR` | Skill execution failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `UNAUTHORIZED` | Invalid or missing auth token |

---

## Rate Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Single Skill | 60 requests | Per minute |
| Skill Chain | 30 requests | Per minute |
| Batch Operations | 10 requests | Per minute |

---

## Chat Agent Commands

Skills can be invoked via natural language:

### Extract Tasks
```
User: "Extract tasks from: Buy milk, call John, prepare presentation"
Agent: [Invokes extract_tasks skill]
```

### Prioritize Task
```
User: "What's the priority for 'finish project report'?"
Agent: [Invokes prioritize_task skill]
```

### Suggest Schedule
```
User: "When should I do my morning standup?"
Agent: [Invokes suggest_schedule skill]
```

### Classify Category
```
User: "What category is 'buy groceries'?"
Agent: [Invokes classify_category skill]
```

### Break Down Task
```
User: "Break down 'deploy to production' into steps"
Agent: [Invokes breakdown_task skill]
```

---

## Python SDK Examples

### Single Skill
```python
import httpx

response = httpx.post(
    f"https://api.example.com/api/{user_id}/skills/extract_tasks",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "input": {
            "text": "Buy milk and call John"
        }
    }
)

result = response.json()
print(result["output"]["tasks"])
```

### Skill Chain
```python
response = httpx.post(
    f"https://api.example.com/api/{user_id}/skills/chain",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "skills": ["extract_tasks", "prioritize_task"],
        "input": {"text": "Urgent: finish report"}
    }
)

result = response.json()
print(result["output"])
```

### Batch Operation
```python
response = httpx.post(
    f"https://api.example.com/api/{user_id}/skills/prioritize_task/batch",
    headers={"Authorization": f"Bearer {token}"},
    json={"task_ids": [1, 2, 3, 4, 5]}
)

results = response.json()["results"]
for r in results:
    print(f"Task {r['task_id']}: {r['priority']}")
```

---

## Performance Guidelines

### Optimization Tips
1. **Batch Operations**: Use batch endpoints for multiple tasks
2. **Caching**: Skill results are cached for 5 minutes
3. **Skill Selection**: Use most specific skill for the job
4. **Chaining**: Chain skills in single request vs multiple calls

### Expected Latencies (p95)
| Skill | Latency |
|-------|---------|
| extract_tasks | < 800ms |
| prioritize_task | < 300ms |
| suggest_schedule | < 250ms |
| classify_category | < 200ms |
| breakdown_task | < 1000ms |
| Skill Chain (3 skills) | < 1500ms |

---

**Version**: 1.0
**Last Updated**: 2025-12-30
