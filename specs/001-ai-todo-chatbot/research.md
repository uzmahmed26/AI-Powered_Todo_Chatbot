# Research & Technology Decisions
**Feature**: AI-Powered Todo Chatbot
**Date**: 2025-12-17

## Overview
This document captures research findings and technology decisions for Phase III implementation. All decisions prioritize MCP-first stateless architecture, <2s response times, and production-grade code quality.

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| Frontend | React + TypeScript | 18+ | Modern UI framework, type safety, component reusability |
| Backend | FastAPI | 0.104+ | Async support, automatic OpenAPI docs, Python ecosystem |
| MCP Server | FastAPI | 0.104+ | Stateless API, HTTP-based MCP implementation |
| Database | PostgreSQL | 15+ | ACID compliance, JSON support, proven scalability |
| AI/LLM | Anthropic Claude | claude-3-5-sonnet | Best NLU, 200k context, function calling |
| Auth | JWT + httpOnly cookies | N/A | Stateless, secure, scalable |
| Rate Limiting | Token bucket + Redis | N/A | Distributed, fair, scalable |
| Deployment | Docker + Docker Compose | Latest | Consistent env, easy local dev |

## Detailed Research Findings

### 1. MCP (Model Context Protocol) Implementation
**Decision**: FastAPI-based HTTP server

**Research Process**:
- Reviewed MCP specification and best practices
- Evaluated gRPC vs REST for tool interface
- Analyzed stateless architecture patterns

**Key Findings**:
- MCP emphasizes stateless, tool-based interactions
- HTTP REST provides language-agnostic, human-readable interface
- FastAPI automatic OpenAPI docs aid development/debugging

**Trade-offs**:
- ✅ Pros: Simple, debuggable, widely supported, async
- ❌ Cons: Slightly less efficient than gRPC (acceptable for use case)

**References**: MCP documentation, FastAPI performance benchmarks

### 2. AI/LLM for Natural Language Understanding
**Decision**: Anthropic Claude API (claude-3-5-sonnet recommended)

**Alternatives Evaluated**:
| Option | Pros | Cons | Cost |
|--------|------|------|------|
| Claude Sonnet | Excellent NLU, 200k context, function calling | Requires API key | $3/1M input, $15/1M output |
| GPT-4 | Similar capabilities | Slightly higher cost | $5/1M input, $15/1M output |
| Llama 3 | Open-source, free | Self-hosting complexity, less capable | Infrastructure cost |

**Selected**: Claude Sonnet
- **Rationale**: Best balance of capability, cost, and ease of integration
- **Function Calling**: Native support for structured outputs (intent extraction)
- **Context Window**: 200k tokens sufficient for conversation history

**Cost Estimation** (10k users, 10 msgs/day/user):
- Average message: 200 tokens input, 100 tokens output
- Daily cost: 10k * 10 * (200 * $0.000003 + 100 * $0.000015) = $21/day = $630/month
- **Mitigation**: Caching common intents reduces cost by ~40%

### 3. Database for Persistent Storage
**Decision**: PostgreSQL 15+

**Requirements Analysis**:
- ACID compliance for todo data integrity
- JSON support for conversation storage (flexible schema)
- Indexing for fast user_id, status, due_date queries
- Concurrent user support (100+ connections)
- Proven scalability (millions of rows)

**Alternatives Rejected**:
- **MySQL**: Less robust JSON support, slightly worse performance for complex queries
- **MongoDB**: NoSQL flexibility not needed, prefer ACID guarantees
- **SQLite**: Single-file database unsuitable for concurrent users

**Schema Strategy**:
- Normalized relational schema for users, todos
- JSON columns for conversation messages (flexible, evolving schema)
- Composite indexes: `(user_id, status)`, `(user_id, due_date)`
- Soft deletes for todos (status='deleted' instead of DELETE)

### 4. Date/Time Parsing Strategy
**Decision**: Hybrid approach (dateparser library + LLM fallback)

**Research Findings**:
- `dateparser` Python library handles common natural language dates
  - "tomorrow", "next Friday", "in 3 days", "Dec 25" ✅
  - Timezone-aware, relative date support
- Edge cases require LLM assistance:
  - "end of this week" (ambiguous: Friday? Sunday?)
  - "next Monday" (this week or next week?)

**Implementation Strategy**:
```python
1. Try dateparser.parse(text, settings={'RELATIVE_BASE': user_timezone})
2. If ambiguous or fails → Ask Claude to clarify/extract date
3. Validate extracted date (not in past for future todos)
4. Store as UTC in database
```

**Performance**: dateparser latency <5ms, LLM fallback adds ~200-500ms

### 5. Authentication & Session Management
**Decision**: JWT (JSON Web Tokens) with httpOnly cookies

**Constitutional Alignment**: Stateless architecture (Principle I)

**Implementation Details**:
- **Token Generation**: HS256 algorithm, secret from env var
- **Token Expiration**: 24 hours (access token), 7 days (refresh token)
- **Storage**: httpOnly cookie (XSS protection) + localStorage fallback
- **Refresh Strategy**: Sliding window (refresh on activity)

**Security Measures**:
- Password hashing: bcrypt (cost factor 12)
- HTTPS required in production
- CORS whitelist (frontend origin only)
- Rate limiting on auth endpoints (10 attempts/hour/IP)

**Alternatives Rejected**:
- **Session-based (Redis)**: Violates stateless principle, adds complexity
- **OAuth2 only**: Requires third-party provider, overkill for MVP

### 6. Rate Limiting Implementation
**Decision**: Token bucket algorithm with Redis backend

**Requirements**:
- 60 requests/minute per authenticated user
- 10 requests/minute per IP (unauthenticated)
- Distributed rate limiting (works across multiple backend instances)

**Technology**: `slowapi` (FastAPI integration) + Redis

**Algorithm**: Token bucket
- Bucket capacity: 60 tokens
- Refill rate: 1 token/second
- Burst support: Yes (full bucket = 60 requests instantly)

**Why not in-memory?**
- Doesn't work across multiple instances (stateless requirement)
- Redis provides shared state for rate limit counters

### 7. Frontend State Management
**Decision**: React hooks (built-in) + custom hooks

**Rationale**:
- Chat application has simple state needs:
  - Messages array (conversation history)
  - Input field value
  - Loading states
  - User authentication status
- Redux/Zustand overkill for this complexity

**Custom Hooks**:
```typescript
useChat(): { messages, sendMessage, isLoading, error }
useTodos(): { todos, refresh, isLoading, error }
useAuth(): { user, login, logout, isAuthenticated }
```

**Performance**: React.memo for message components (prevent re-renders)

### 8. Deployment & Containerization
**Decision**: Docker + Docker Compose (MVP), Kubernetes (bonus P3)

**MVP Architecture**:
- 4 containers: frontend, backend, mcp-server, postgresql
- Docker Compose orchestration (single command startup)
- Nginx reverse proxy (SSL termination, routing)

**Production/Bonus (P3)**:
- Kubernetes (GKE/EKS/AKS)
- Horizontal Pod Autoscaling (HPA)
- Managed PostgreSQL (Cloud SQL/RDS)
- Redis cluster for rate limiting
- CI/CD: GitHub Actions

## Performance Optimization Research

### Database Query Optimization
**Indexes to Create**:
```sql
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todos_user_status_due ON todos(user_id, status, due_date);
```

**Connection Pooling**:
- SQLAlchemy async pool: 5-10 connections per instance
- Connection timeout: 30s
- Pool recycle: 3600s (1 hour)

### AI Response Optimization
**Caching Strategy**:
- Cache key: hash(user_id + message_text)
- TTL: 5 minutes for common intents ("show tasks", "list todos")
- Hit rate goal: 30-40%
- Estimated savings: $250/month at 10k users

**Streaming Responses** (Future Enhancement):
- Use Claude streaming API for faster perceived response
- Send tokens as they arrive (WebSocket or SSE)
- Improves UX even if total latency same

### API Response Optimization
- GZIP compression: Enabled for all text responses (HTML, JSON, JS)
- Pagination: Max 50 todos per page (limit query size)
- Lazy loading: Completed todos loaded on demand only

## Security Research

### OWASP Top 10 Compliance

| Vulnerability | Mitigation |
|---------------|------------|
| A01: Broken Access Control | User isolation (user_id in JWT), authorization checks on every MCP call |
| A02: Cryptographic Failures | HTTPS required, bcrypt for passwords, JWT secrets in env vars |
| A03: Injection | Pydantic validation, SQLAlchemy ORM (parameterized queries), React auto-escaping |
| A04: Insecure Design | MCP stateless architecture, rate limiting, input validation |
| A05: Security Misconfiguration | CORS whitelist, CSP headers, security headers (X-Frame-Options, etc.) |
| A06: Vulnerable Components | Dependabot alerts, regular dependency updates, minimal dependencies |
| A07: Auth Failures | bcrypt cost 12, JWT expiration, httpOnly cookies, rate limiting on auth |
| A08: Data Integrity Failures | Database transactions, soft deletes, audit logs |
| A09: Logging Failures | Structured JSON logging, request tracing, no sensitive data in logs |
| A10: SSRF | Input validation, no user-controlled URLs in backend requests |

### Input Validation Strategy
**Layer 1: Pydantic Models** (Backend API)
```python
class ChatMessageRequest(BaseModel):
    message: str = Field(max_length=2000, min_length=1)

class CreateTodoRequest(BaseModel):
    title: str = Field(max_length=200, min_length=1)
    description: Optional[str] = Field(max_length=5000)
    due_date: Optional[date]
```

**Layer 2: Business Logic Validation**
- User exists and is authenticated
- User owns the resource (todo belongs to user_id)
- Dates are valid (not in far past, not too far in future)

**Layer 3: Database Constraints**
- NOT NULL constraints
- CHECK constraints (e.g., due_date > created_at)
- Foreign key constraints (referential integrity)

## Cost Analysis

### Infrastructure Costs (Estimated, 10k users)
| Service | Provider | Cost/Month |
|---------|----------|------------|
| PostgreSQL | DigitalOcean Managed DB | $60 |
| Backend + MCP Server | 2x DigitalOcean Droplets (4GB) | $48 |
| Frontend | Vercel/Netlify Free Tier | $0 |
| Redis | DigitalOcean Managed | $15 |
| Claude API | Anthropic | $630 (with caching: $380) |
| **Total** | | **$743/month** ($503 with caching) |

**Per User Cost**: $0.05-0.07/month (sustainable at $5-10/user/month pricing)

### Scaling Projections
| Users | Infrastructure | AI API | Total/Month |
|-------|---------------|--------|-------------|
| 1,000 | $123 | $63 | $186 |
| 10,000 | $123 | $380 (cached) | $503 |
| 100,000 | $500 (k8s cluster) | $3,800 | $4,300 |

## Conclusion

All technology decisions align with constitutional principles:
✅ **MCP-First Stateless**: FastAPI MCP server, JWT auth, Redis rate limiting
✅ **<2s Response Time**: Optimized queries, caching, async processing
✅ **Security & Privacy**: OWASP compliance, input validation, user isolation
✅ **Scalability**: Stateless architecture, horizontal scaling ready
✅ **Observability**: Structured logging, request tracing, metrics

**Readiness**: All technical unknowns resolved. Ready to proceed to data model and contract design (Phase 1).
