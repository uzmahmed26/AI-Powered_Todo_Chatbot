# Feature Specification: JWT Authentication System

## Metadata
- **Feature ID**: 007-jwt-authentication
- **Priority**: P1 (MVP - Security Critical)
- **Status**: Draft
- **Created**: 2025-12-30
- **Tech Stack**: FastAPI (Backend) + React/Vite (Frontend)

---

## Overview

Add JWT-based authentication to the AI-Powered Todo Chatbot project to secure user data and API endpoints.

### Context
Currently, the application uses a demo user (`demo-user`) with no authentication. This specification outlines the implementation of a complete JWT authentication system with signup, signin, and route protection.

### Goals
- ✅ Secure signup and signin with email/password
- ✅ JWT token-based authentication (access + refresh tokens)
- ✅ Protected API routes requiring valid JWT
- ✅ User isolation (each user sees only their own todos)
- ✅ Frontend auth pages (Signup, Signin)
- ✅ Protected routes on frontend
- ✅ Compatible with existing SpecKit Plus structure

### Non-Goals
- ❌ OAuth/Social login (Phase 2)
- ❌ Email verification (Phase 2)
- ❌ Password reset flow (Phase 2)
- ❌ Two-factor authentication (Phase 2)
- ❌ Migration to Next.js (separate decision)

---

## User Stories

### User Story 1: User Signup (P1 - MVP)
**As a** new user
**I want to** create an account with email and password
**So that** I can access the todo chatbot with my own isolated data

**Acceptance Criteria**:
- User can visit `/signup` page
- Form validates email format and password strength
- Password must be 8+ chars with uppercase, lowercase, number
- Successful signup creates user in database
- Password stored as bcrypt hash (never plaintext)
- Returns JWT access token + refresh token
- Redirects to chat page after successful signup
- Shows error messages for duplicate email or validation failures

**API Contract**:
```http
POST /api/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe"
}

Response 201:
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2025-12-30T10:00:00Z"
  },
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}

Response 400:
{
  "detail": "Email already registered"
}
```

---

### User Story 2: User Signin (P1 - MVP)
**As a** registered user
**I want to** sign in with my email and password
**So that** I can access my todo conversations

**Acceptance Criteria**:
- User can visit `/signin` page
- Form accepts email and password
- Invalid credentials show clear error message
- Successful signin returns JWT tokens
- Tokens stored in localStorage/httpOnly cookie
- Redirects to chat page after successful signin
- "Remember me" option for extended session

**API Contract**:
```http
POST /api/auth/signin
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response 200:
{
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "full_name": "John Doe"
  },
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}

Response 401:
{
  "detail": "Invalid email or password"
}
```

---

### User Story 3: Protected API Routes (P1 - MVP)
**As a** system administrator
**I want** all todo/chat API routes protected by JWT
**So that** only authenticated users can access their data

**Acceptance Criteria**:
- All `/api/{user_id}/chat` routes require valid JWT
- All MCP tool calls (add_task, list_tasks, etc.) require authentication
- JWT validates user_id matches token's user_id
- Expired tokens return 401 Unauthorized
- Missing tokens return 401 Unauthorized
- Invalid tokens return 401 Unauthorized
- Token includes: user_id, email, expiry (15 min for access, 7 days for refresh)

**Protected Routes**:
- `POST /api/{user_id}/chat` → Requires JWT with matching user_id
- `GET /api/{user_id}/tasks` → Requires JWT (future endpoint)
- All existing routes that accept user_id parameter

---

### User Story 4: Token Refresh (P1 - MVP)
**As a** authenticated user
**I want** my session to automatically refresh
**So that** I don't get logged out while actively using the app

**Acceptance Criteria**:
- Access token expires after 15 minutes
- Refresh token expires after 7 days
- Frontend automatically calls refresh endpoint when access token expires
- Refresh endpoint accepts refresh token, returns new access token
- Invalid refresh token logs user out

**API Contract**:
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}

Response 401:
{
  "detail": "Invalid or expired refresh token"
}
```

---

### User Story 5: Frontend Protected Routes (P1 - MVP)
**As a** user
**I want** to be redirected to signin if not authenticated
**So that** I cannot access protected pages without logging in

**Acceptance Criteria**:
- Unauthenticated users visiting `/` redirect to `/signin`
- Token stored securely (localStorage or httpOnly cookie)
- Auth context/hook provides current user info
- Logout clears tokens and redirects to signin
- Protected routes check token validity before rendering

---

## Technical Design

### Backend Architecture

#### Database Models

**User Model** (`backend/src/models/user.py`):
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime
    updated_at: datetime
```

#### JWT Configuration

- **Algorithm**: HS256
- **Access Token Expiry**: 15 minutes
- **Refresh Token Expiry**: 7 days
- **Secret Key**: Environment variable `JWT_SECRET_KEY`
- **Refresh Secret Key**: Environment variable `JWT_REFRESH_SECRET_KEY`

#### Password Security

- **Hashing Algorithm**: bcrypt
- **Salt Rounds**: 12
- **Password Requirements**:
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 number
  - At least 1 special character

---

### Frontend Architecture

#### Auth Pages

1. **Signup Page** (`frontend/src/pages/SignupPage.tsx`)
   - Email input (validated)
   - Password input (strength indicator)
   - Confirm password input
   - Full name input
   - Submit button
   - Link to signin page

2. **Signin Page** (`frontend/src/pages/SigninPage.tsx`)
   - Email input
   - Password input
   - Remember me checkbox
   - Submit button
   - Link to signup page

#### Auth Context

**AuthContext** (`frontend/src/context/AuthContext.tsx`):
```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  signout: () => void;
  refreshToken: () => Promise<void>;
}
```

#### Protected Route Component

```typescript
<ProtectedRoute>
  <SmartTodoApp />
</ProtectedRoute>
```

---

## API Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/signup` | No | Create new user account |
| POST | `/api/auth/signin` | No | Authenticate user |
| POST | `/api/auth/refresh` | Yes (Refresh) | Get new access token |
| POST | `/api/auth/signout` | Yes | Invalidate refresh token |
| GET | `/api/auth/me` | Yes | Get current user info |
| POST | `/api/{user_id}/chat` | Yes | Protected chat endpoint |

---

## Security Considerations

### Backend Security
- ✅ Never log passwords or tokens
- ✅ Use environment variables for secrets
- ✅ Validate JWT signature and expiry
- ✅ Hash passwords with bcrypt (never store plaintext)
- ✅ Sanitize user inputs
- ✅ Rate limit auth endpoints (max 5 attempts per minute)
- ✅ HTTPS only in production
- ✅ CORS configured for allowed origins only

### Frontend Security
- ✅ Store tokens in httpOnly cookies (preferred) or localStorage
- ✅ Clear tokens on logout
- ✅ Auto-refresh tokens before expiry
- ✅ Redirect to signin on 401 responses
- ✅ Never expose tokens in URLs or logs
- ✅ Validate email format client-side
- ✅ Show password strength indicator

---

## Migration Strategy

### Phase 1: Implement Auth (This Spec)
1. Add User model and migration
2. Implement JWT utilities
3. Create auth endpoints
4. Add JWT middleware to protect routes
5. Build frontend auth pages
6. Implement auth context and protected routes

### Phase 2: Migrate Existing Data
1. Create migration script to assign demo-user data to real users
2. Update existing conversations and tasks with user_id references
3. Remove demo-user fallback

### Phase 3: Enhanced Features (Future)
- Email verification
- Password reset flow
- OAuth providers (Google, GitHub)
- Two-factor authentication

---

## Success Criteria

### Functional Requirements
- ✅ Users can signup with email/password
- ✅ Users can signin with valid credentials
- ✅ Invalid credentials show clear error messages
- ✅ All chat and task API routes require valid JWT
- ✅ Tokens auto-refresh before expiry
- ✅ Users can logout and tokens are cleared
- ✅ Each user sees only their own todos and conversations

### Non-Functional Requirements
- ✅ Signup/Signin completes in < 2 seconds (p95)
- ✅ JWT validation adds < 50ms overhead per request
- ✅ Password hashing uses bcrypt with 12 rounds
- ✅ Access tokens expire in 15 minutes
- ✅ Refresh tokens expire in 7 days
- ✅ Auth pages are responsive (mobile + desktop)
- ✅ Error messages are user-friendly (no technical jargon)

---

## Dependencies

### Backend
- `python-jose[cryptography]` - JWT encoding/decoding
- `passlib[bcrypt]` - Password hashing
- `python-multipart` - Form data handling
- `pydantic[email]` - Email validation

### Frontend
- `react-router-dom` - Client-side routing
- `axios` - HTTP client (already installed)
- `jwt-decode` - JWT decoding on client
- `zod` - Form validation

---

## Open Questions

1. **Token Storage**: Use localStorage or httpOnly cookies?
   - **Decision**: Use httpOnly cookies for production (more secure), localStorage for development simplicity

2. **Password Reset**: Include in Phase 1 or defer to Phase 2?
   - **Decision**: Defer to Phase 2 (not MVP critical)

3. **Email Verification**: Required for MVP?
   - **Decision**: Defer to Phase 2 (nice-to-have)

4. **Existing Demo User**: What happens to demo-user data?
   - **Decision**: Keep for development, migrate to real users in Phase 2

---

## Next Steps

1. Review and approve this specification
2. Create detailed implementation plan (`plan.md`)
3. Break down into atomic tasks (`tasks.md`)
4. Implement backend auth system
5. Implement frontend auth pages
6. Test end-to-end authentication flow
7. Deploy and verify in production
