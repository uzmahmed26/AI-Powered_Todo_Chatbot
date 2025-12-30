# Agent Skills for Todo Operations - Specification

## 1. Overview

**Feature**: Reusable Agent Skills for intelligent todo task operations

**Purpose**: Create modular, composable skills that encapsulate specific AI capabilities for task management, usable by both the chatbot agent and direct API calls.

**Value Proposition**:
- **Modularity**: Skills are independent, testable units
- **Reusability**: Same skill works in chat, API, and batch operations
- **Composability**: Skills can be chained and combined
- **Maintainability**: Single implementation for each capability
- **Extensibility**: Easy to add new skills without modifying core agent

---

## 2. Scope

### In Scope
1. **Core Skills**:
   - Task Extraction (from natural language or documents)
   - Smart Prioritization (based on urgency, deadlines, context)
   - Intelligent Scheduling (suggest due dates/times)
   - Task Breakdown (split complex tasks into subtasks)
   - Category Classification (auto-assign categories)

2. **Skill Infrastructure**:
   - Skill registry and loader
   - Skill execution framework
   - Input/output schemas for each skill
   - Skill chaining mechanism
   - Error handling and fallbacks

3. **Integration Points**:
   - Chat agent integration (skills callable via natural language)
   - REST API endpoints (direct skill invocation)
   - Batch processing (apply skills to multiple tasks)
   - Skill composition (pipe skills together)

4. **SpecKit Plus Compliance**:
   - Skills follow spec-driven development
   - Documentation for each skill
   - Test coverage for all skills
   - Type safety with Pydantic

### Out of Scope
- Complex ML model training (use pre-trained models or heuristics)
- Real-time collaborative features
- Mobile app integration
- Third-party calendar sync (future enhancement)

---

## 3. Agent Skills Architecture

### 3.1 Skill Definition

Each skill is a **stateless, composable unit** with:

```python
class Skill(BaseModel):
    """Base class for all agent skills."""

    name: str                    # Unique skill identifier
    description: str             # What the skill does
    input_schema: Type[BaseModel]  # Pydantic schema for inputs
    output_schema: Type[BaseModel] # Pydantic schema for outputs

    async def execute(self, input_data: BaseModel) -> BaseModel:
        """Execute the skill with validated input."""
        pass
```

### 3.2 Skill Types

**1. Extraction Skills** (Text → Structured Data)
- Extract tasks from natural language
- Extract tasks from emails, documents
- Extract metadata (priority, category, due date)

**2. Enhancement Skills** (Task → Enhanced Task)
- Prioritize based on context
- Suggest due dates/times
- Auto-categorize tasks
- Add descriptions/details

**3. Transformation Skills** (Task → Tasks)
- Break down complex tasks
- Generate subtasks
- Create recurring patterns

**4. Analysis Skills** (Tasks → Insights)
- Workload analysis
- Deadline conflicts detection
- Productivity patterns

### 3.3 Skill Execution Flow

```
User Input (Chat/API)
    ↓
Skill Selector (determines which skills to use)
    ↓
Skill Chain (executes skills in sequence)
    ↓
Skill Executor (runs each skill with validation)
    ↓
Result Aggregator (combines skill outputs)
    ↓
Response Formatter (natural language or JSON)
    ↓
User Output
```

---

## 4. Core Skills Specification

### 4.1 Task Extraction Skill

**Name**: `extract_tasks`

**Description**: Extract one or more tasks from natural language text, emails, or documents.

**Input Schema**:
```python
class ExtractTasksInput(BaseModel):
    text: str                          # Input text to extract from
    context: Optional[str] = None      # Additional context
    max_tasks: int = 10                # Maximum tasks to extract
```

**Output Schema**:
```python
class ExtractedTask(BaseModel):
    title: str
    description: Optional[str] = None
    confidence: float                  # 0.0 to 1.0

class ExtractTasksOutput(BaseModel):
    tasks: List[ExtractedTask]
    count: int
```

**Algorithm**:
1. Use OpenAI GPT-4 with structured output to parse text
2. Identify action items, todos, and commitments
3. Extract task titles and optional descriptions
4. Return confidence score for each extraction

**Examples**:
```
Input: "I need to buy groceries tomorrow and call the dentist to schedule an appointment"
Output: [
  {title: "Buy groceries", description: "Due tomorrow", confidence: 0.95},
  {title: "Call dentist to schedule appointment", confidence: 0.90}
]
```

---

### 4.2 Smart Prioritization Skill

**Name**: `prioritize_task`

**Description**: Intelligently assign priority (high/medium/low) based on keywords, deadlines, and context.

**Input Schema**:
```python
class PrioritizeTaskInput(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    category: Optional[str] = None
    context: Optional[str] = None      # User's current workload
```

**Output Schema**:
```python
class PrioritizeTaskOutput(BaseModel):
    priority: Literal["high", "medium", "low"]
    reasoning: str                     # Why this priority was chosen
    confidence: float
```

**Algorithm**:
1. **Keyword Analysis**: Detect urgency keywords (urgent, ASAP, critical, important)
2. **Deadline Proximity**: Tasks due within 24h → high, 3 days → medium, 7+ days → low
3. **Category Heuristics**: Work + deadline → higher priority than personal
4. **AI Enhancement**: Use GPT-4 to refine priority with context
5. **Confidence Scoring**: Return confidence in the assignment

**Priority Rules**:
- Keywords: "urgent", "critical", "ASAP", "important" → high
- Due < 24 hours → high
- Due 1-3 days → medium
- Due > 7 days → low
- Work category + deadline → boost priority
- Personal category + no deadline → low

---

### 4.3 Intelligent Scheduling Skill

**Name**: `suggest_schedule`

**Description**: Suggest optimal due date and time for a task based on title, description, and user's schedule.

**Input Schema**:
```python
class SuggestScheduleInput(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    relative_date: Optional[str] = None  # "tomorrow", "next week", "in 3 days"
```

**Output Schema**:
```python
class SuggestScheduleOutput(BaseModel):
    suggested_due_date: datetime
    reasoning: str
    time_of_day: Literal["morning", "afternoon", "evening", "specific"]
    confidence: float
```

**Algorithm**:
1. **Parse Relative Dates**: "tomorrow" → today + 1 day, "next week" → today + 7 days
2. **Time-of-Day Heuristics**:
   - Morning tasks: "standup", "meeting", "email"
   - Evening tasks: "review", "plan", "prepare"
   - Specific time: "call", "appointment"
3. **Category-Based Defaults**:
   - Work tasks: Business hours (9 AM - 5 PM)
   - Personal tasks: Evening (6 PM - 9 PM)
   - Health/Fitness: Morning (6 AM - 9 AM)
4. **Priority Adjustment**: High priority → sooner, Low priority → later

**Examples**:
```
Input: {title: "Morning standup", category: "work"}
Output: {
  suggested_due_date: "2025-01-02T09:00:00Z",
  reasoning: "Work meetings typically happen in morning",
  time_of_day: "morning",
  confidence: 0.85
}
```

---

### 4.4 Task Breakdown Skill

**Name**: `breakdown_task`

**Description**: Break a complex task into smaller, actionable subtasks.

**Input Schema**:
```python
class BreakdownTaskInput(BaseModel):
    title: str
    description: Optional[str] = None
    max_subtasks: int = 5
```

**Output Schema**:
```python
class Subtask(BaseModel):
    title: str
    description: Optional[str] = None
    order: int                         # Sequence number
    estimated_duration: Optional[str] = None  # "30m", "2h", "1d"

class BreakdownTaskOutput(BaseModel):
    subtasks: List[Subtask]
    total_estimated_duration: Optional[str] = None
```

**Algorithm**:
1. Use GPT-4 to analyze task complexity
2. Identify logical steps and dependencies
3. Generate ordered subtasks
4. Estimate duration for each step (optional)
5. Return maximum of `max_subtasks` items

**Examples**:
```
Input: {title: "Deploy new feature to production"}
Output: {
  subtasks: [
    {title: "Run all tests", order: 1, estimated_duration: "30m"},
    {title: "Create pull request", order: 2, estimated_duration: "15m"},
    {title: "Get code review approval", order: 3, estimated_duration: "2h"},
    {title: "Merge to main branch", order: 4, estimated_duration: "5m"},
    {title: "Deploy to production", order: 5, estimated_duration: "30m"}
  ],
  total_estimated_duration: "3h20m"
}
```

---

### 4.5 Category Classification Skill

**Name**: `classify_category`

**Description**: Automatically assign a category to a task based on its title and description.

**Input Schema**:
```python
class ClassifyCategoryInput(BaseModel):
    title: str
    description: Optional[str] = None
```

**Output Schema**:
```python
class ClassifyCategoryOutput(BaseModel):
    category: Literal["work", "home", "study", "personal", "shopping", "health", "fitness"]
    confidence: float
    reasoning: str
```

**Algorithm**:
1. **Keyword Matching**:
   - Work: "meeting", "report", "project", "deadline", "presentation"
   - Shopping: "buy", "purchase", "groceries", "order"
   - Health: "doctor", "appointment", "medication", "checkup"
   - Fitness: "gym", "workout", "exercise", "run"
   - Study: "study", "homework", "assignment", "exam"
   - Home: "clean", "fix", "repair", "organize"
2. **AI Classification**: Use GPT-4 for ambiguous cases
3. **Default**: "personal" if uncertain

---

## 5. Skill Infrastructure

### 5.1 Skill Registry

**File**: `backend/src/skills/registry.py`

```python
class SkillRegistry:
    """Central registry for all agent skills."""

    def __init__(self):
        self._skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """Get skill by name."""
        return self._skills[name]

    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self._skills.keys())
```

### 5.2 Skill Executor

**File**: `backend/src/skills/executor.py`

```python
class SkillExecutor:
    """Execute skills with validation and error handling."""

    async def execute(
        self,
        skill_name: str,
        input_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Execute a skill with input validation."""
        # Get skill from registry
        # Validate input against schema
        # Execute skill
        # Validate output against schema
        # Return result
```

### 5.3 Skill Chaining

**File**: `backend/src/skills/chain.py`

```python
class SkillChain:
    """Chain multiple skills together."""

    def __init__(self, skills: List[str]):
        self.skills = skills

    async def execute(self, initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute skills in sequence, passing output to next input."""
        # Execute first skill
        # Pass output to next skill
        # Continue until all skills executed
        # Return final output
```

---

## 6. API Integration

### 6.1 Skill Endpoints

**Base Path**: `/api/{user_id}/skills`

#### Execute Single Skill
```http
POST /api/{user_id}/skills/{skill_name}
Content-Type: application/json

{
  "input": {
    "text": "I need to buy groceries and call the dentist"
  }
}

Response:
{
  "success": true,
  "skill": "extract_tasks",
  "output": {
    "tasks": [
      {"title": "Buy groceries", "confidence": 0.95},
      {"title": "Call dentist", "confidence": 0.90}
    ],
    "count": 2
  }
}
```

#### Execute Skill Chain
```http
POST /api/{user_id}/skills/chain
Content-Type: application/json

{
  "skills": ["extract_tasks", "prioritize_task", "classify_category"],
  "input": {
    "text": "Urgent: finish project report by tomorrow"
  }
}

Response:
{
  "success": true,
  "chain": ["extract_tasks", "prioritize_task", "classify_category"],
  "output": {
    "title": "Finish project report",
    "priority": "high",
    "category": "work",
    "due_date": "2025-01-02T23:59:59Z"
  }
}
```

#### Batch Apply Skill
```http
POST /api/{user_id}/skills/{skill_name}/batch
Content-Type: application/json

{
  "task_ids": [1, 2, 3, 4, 5]
}

Response:
{
  "success": true,
  "skill": "prioritize_task",
  "results": [
    {"task_id": 1, "priority": "high", "updated": true},
    {"task_id": 2, "priority": "medium", "updated": true},
    ...
  ]
}
```

---

## 7. Chat Agent Integration

### 7.1 Skill Invocation via Chat

Users can invoke skills naturally through chat:

```
User: "Extract tasks from this: I need to buy milk, call John, and prepare presentation"
Agent: [Calls extract_tasks skill]
Agent: "I found 3 tasks:
  1. Buy milk
  2. Call John
  3. Prepare presentation

  Would you like me to add these to your task list?"

User: "Yes, and prioritize them"
Agent: [Calls add_task + prioritize_task skills]
Agent: "Added 3 tasks:
  ✓ Buy milk (low priority)
  ✓ Call John (medium priority)
  ✓ Prepare presentation (high priority - work related)"
```

### 7.2 Automatic Skill Selection

The agent automatically selects relevant skills based on user intent:

```python
# In agent.py system prompt
"""
When appropriate, use these skills to enhance task management:

- extract_tasks: When user provides text with multiple tasks
- prioritize_task: When creating tasks or when user asks "what's important"
- suggest_schedule: When user asks "when should I do this"
- breakdown_task: When user says "break this down" or task seems complex
- classify_category: When adding tasks without explicit category
"""
```

---

## 8. Implementation Plan

### Phase 1: Core Infrastructure (2-3 hours)
1. Create `backend/src/skills/` package structure
2. Implement base `Skill` class
3. Create `SkillRegistry` singleton
4. Implement `SkillExecutor` with validation
5. Add skill schemas module

### Phase 2: Core Skills (4-5 hours)
1. Implement `extract_tasks` skill
2. Implement `prioritize_task` skill
3. Implement `suggest_schedule` skill
4. Implement `classify_category` skill
5. Implement `breakdown_task` skill
6. Add unit tests for each skill

### Phase 3: API Integration (2-3 hours)
1. Create `/api/{user_id}/skills/*` routes
2. Add single skill execution endpoint
3. Add skill chain execution endpoint
4. Add batch skill application endpoint
5. Add API documentation

### Phase 4: Chat Agent Integration (1-2 hours)
1. Update agent system prompt with skills
2. Register skills with OpenAI function calling
3. Add skill invocation logic in agent
4. Test skill invocation via chat

### Phase 5: Advanced Features (2-3 hours)
1. Implement `SkillChain` for composability
2. Add caching for skill results
3. Add skill performance metrics
4. Create skill usage analytics

**Total Estimated Time**: 11-16 hours

---

## 9. File Structure

```
backend/src/skills/
├── __init__.py                 # Package exports
├── base.py                     # Base Skill class
├── registry.py                 # SkillRegistry singleton
├── executor.py                 # SkillExecutor with validation
├── chain.py                    # SkillChain for composition
├── schemas.py                  # Input/Output schemas for all skills
│
├── extraction/
│   ├── __init__.py
│   └── extract_tasks.py        # Task extraction skill
│
├── enhancement/
│   ├── __init__.py
│   ├── prioritize_task.py      # Prioritization skill
│   ├── suggest_schedule.py     # Scheduling skill
│   └── classify_category.py    # Category classification skill
│
└── transformation/
    ├── __init__.py
    └── breakdown_task.py       # Task breakdown skill

backend/src/api/routes/
└── skills.py                   # NEW: Skill API routes

specs/010-agent-skills/
├── spec.md                     # This file
├── IMPLEMENTATION_GUIDE.md     # Step-by-step guide
├── QUICK_REFERENCE.md          # Skill API reference
└── README.md                   # Feature overview
```

---

## 10. Testing Strategy

### Unit Tests
- Test each skill independently
- Mock OpenAI API calls
- Validate input/output schemas
- Test error cases

### Integration Tests
- Test skill execution via API
- Test skill chaining
- Test batch operations
- Test agent integration

### End-to-End Tests
- Test skills via chat interface
- Test complete workflows
- Test skill composition

---

## 11. Success Metrics

### Functionality
- ✅ All 5 core skills implemented and tested
- ✅ Skills callable via API and chat
- ✅ Skill chaining works correctly
- ✅ 90%+ accuracy on skill outputs

### Performance
- ✅ Skills execute in < 2 seconds (95th percentile)
- ✅ Batch operations scale to 100+ tasks
- ✅ OpenAI API usage optimized (caching, batching)

### Usability
- ✅ Skills enhance chat experience
- ✅ API documentation complete
- ✅ Error messages are clear and actionable

---

## 12. Future Enhancements

### Advanced Skills
- **Time Blocking**: Suggest optimal time slots based on calendar
- **Dependency Detection**: Identify task dependencies
- **Workload Balancing**: Distribute tasks evenly across days
- **Conflict Resolution**: Detect and resolve scheduling conflicts

### Skill Ecosystem
- **Custom Skills**: Users can define custom skills
- **Skill Marketplace**: Share and discover community skills
- **Skill Analytics**: Track skill usage and effectiveness

### AI Improvements
- **Fine-tuned Models**: Train custom models for specific skills
- **User Learning**: Adapt skills to individual user patterns
- **Context Awareness**: Use user's full task history for better predictions

---

## 13. Security & Privacy

### Data Handling
- Skills process user data in-memory only
- No persistent storage of skill inputs/outputs (except audit logs)
- OpenAI API calls follow data retention policies

### Access Control
- Skills respect user_id isolation
- API endpoints require authentication
- Batch operations limited by user permissions

### Rate Limiting
- Skill API endpoints rate-limited per user
- OpenAI API usage monitored and capped

---

## 14. Acceptance Criteria

### Must Have
- [ ] All 5 core skills implemented
- [ ] Skill registry and executor functional
- [ ] API endpoints for single skill execution
- [ ] Chat agent can invoke skills
- [ ] Input/output validation working
- [ ] Error handling and logging complete
- [ ] Unit tests with 80%+ coverage
- [ ] Documentation complete

### Should Have
- [ ] Skill chaining implemented
- [ ] Batch skill application working
- [ ] Skill performance metrics
- [ ] Integration tests passing
- [ ] API documentation auto-generated

### Nice to Have
- [ ] Skill result caching
- [ ] Skill usage analytics
- [ ] Advanced skills (time blocking, dependencies)
- [ ] Custom skill support

---

## 15. Dependencies

### Technology Stack
- **OpenAI GPT-4**: For NLP-heavy skills (extraction, breakdown)
- **Pydantic**: Input/output validation
- **FastAPI**: API routes
- **SQLModel**: Task database access (for batch operations)

### External Services
- OpenAI API (required)
- None others

### Internal Dependencies
- Existing task models and schemas
- Chat agent infrastructure
- Authentication system

---

## Appendix: Skill Catalog

| Skill Name | Type | Input | Output | Use Case |
|------------|------|-------|--------|----------|
| extract_tasks | Extraction | Text | List[Task] | Parse emails, notes |
| prioritize_task | Enhancement | Task | Priority | Auto-prioritize tasks |
| suggest_schedule | Enhancement | Task | DateTime | Suggest due dates |
| classify_category | Enhancement | Task | Category | Auto-categorize tasks |
| breakdown_task | Transformation | Task | List[Subtask] | Split complex tasks |

---

**Version**: 1.0
**Status**: Draft
**Last Updated**: 2025-12-30
