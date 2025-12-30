# JWT Authentication Implementation Steps

Complete step-by-step guide to add JWT authentication to your AI-Powered Todo project.

---

## Prerequisites

✅ Backend: FastAPI + SQLModel + PostgreSQL (already setup)
✅ Frontend: React + Vite + TypeScript (already setup)
✅ Project structure: SpecKit Plus compatible

---

## Phase 1: Backend Implementation

### Step 1: Install Required Dependencies

```bash
cd backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email]
pip freeze > requirements.txt
```

**Packages**:
- `python-jose` - JWT encoding/decoding
- `passlib` - Password hashing (bcrypt)
- `python-multipart` - Form data handling
- `pydantic[email]` - Email validation

---

### Step 2: Update Environment Variables

**File**: `backend/.env`

```bash
# Existing variables...
DATABASE_URL=postgresql+asyncpg://...
OPENAI_API_KEY=sk-...

# Add these new variables:
JWT_SECRET_KEY=your-super-secret-key-here-min-32-chars
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Generate secure secret keys**:
```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -hex 32
```

---

### Step 3: Create User Model

**File**: `backend/src/models/user.py`

```python
"""User model for authentication."""

from datetime import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel, Column, DateTime
from sqlalchemy.sql import func


class User(SQLModel, table=True):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier (UUID)",
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique)",
    )
    hashed_password: str = Field(
        max_length=255,
        description="Bcrypt hashed password",
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's full name",
    )
    is_active: bool = Field(
        default=True,
        description="Whether user account is active",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
        description="Account creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
        description="Last update timestamp",
    )

    class Config:
        """SQLModel configuration."""

        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
            }
        }
```

**Update**: `backend/src/models/__init__.py`

```python
from .user import User
from .task import Task
from .conversation import Conversation
from .message import Message

__all__ = ["User", "Task", "Conversation", "Message"]
```

---

### Step 4: Create Database Migration

```bash
cd backend
python -m alembic revision --autogenerate -m "add users table for authentication"
```

**Review the generated migration** in `backend/alembic/versions/`, then:

```bash
python -m alembic upgrade head
```

---

### Step 5: Create JWT Utilities

**File**: `backend/src/auth/jwt.py`

```python
"""JWT token utilities for authentication."""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration from environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", "dev-refresh-key-change")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenData(BaseModel):
    """Token payload data."""

    user_id: str
    email: str
    exp: Optional[datetime] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user_id and email

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.

    Args:
        data: Dictionary containing user_id and email

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string
        token_type: "access" or "refresh"

    Returns:
        TokenData if valid, None if invalid
    """
    try:
        secret = SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])

        # Validate token type
        if payload.get("type") != token_type:
            return None

        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            return None

        return TokenData(user_id=user_id, email=email, exp=payload.get("exp"))

    except JWTError:
        return None
```

---

### Step 6: Create Auth Dependencies

**File**: `backend/src/auth/dependencies.py`

```python
"""FastAPI dependencies for authentication."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from ..database.engine import get_async_session
from ..models.user import User
from .jwt import decode_token
from sqlmodel import select

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Authorization header with Bearer token
        session: Database session

    Returns:
        User object if authenticated

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Decode token
    token_data = decode_token(credentials.credentials, token_type="access")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await session.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to ensure user is active.

    Args:
        current_user: Current user from get_current_user

    Returns:
        User object if active

    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user
```

---

### Step 7: Create Auth Pydantic Schemas

**File**: `backend/src/auth/schemas.py`

```python
"""Pydantic schemas for authentication."""

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserSignup(BaseModel):
    """User signup request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (8-100 chars)")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v


class UserSignin(BaseModel):
    """User signin request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User response schema (no password)."""

    id: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Authentication token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str
```

---

### Step 8: Create Auth Routes

**File**: `backend/src/api/routes/auth.py`

```python
"""Authentication routes for signup, signin, and token management."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import logging

from ...database.engine import get_async_session
from ...models.user import User
from ...auth.schemas import (
    UserSignup,
    UserSignin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
)
from ...auth.jwt import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ...auth.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignup,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """
    Create a new user account.

    Args:
        user_data: User signup information
        session: Database session

    Returns:
        TokenResponse with access/refresh tokens and user info

    Raises:
        HTTPException: 400 if email already registered
    """
    # Check if email already exists
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    logger.info(f"New user created: {new_user.email}")

    # Generate tokens
    token_data = {"user_id": new_user.id, "email": new_user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(
    credentials: UserSignin,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TokenResponse:
    """
    Authenticate user and return JWT tokens.

    Args:
        credentials: User email and password
        session: Database session

    Returns:
        TokenResponse with access/refresh tokens

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email
    result = await session.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    # Verify credentials
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    logger.info(f"User signed in: {user.email}")

    # Generate tokens
    token_data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=dict)
async def refresh_access_token(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> dict:
    """
    Refresh access token using refresh token.

    Args:
        request: Refresh token
        session: Database session

    Returns:
        New access token

    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    # Decode refresh token
    token_data = decode_token(request.refresh_token, token_type="refresh")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    result = await session.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Generate new access token
    new_token_data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(new_token_data)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Sign out current user (client should delete tokens).

    Note: Since JWT is stateless, actual logout happens on client side.
    This endpoint is for consistency and future token blacklisting.
    """
    logger.info(f"User signed out: {current_user.email}")
    return None
```

---

### Step 9: Register Auth Routes

**File**: `backend/src/api/app.py`

Add this after existing route registrations:

```python
# Import auth router
from .routes import auth

# Register auth routes
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

logger.info("Auth API routes registered at /api/auth/*")
```

---

### Step 10: Protect Existing Chat Route

**File**: `backend/src/api/routes/chat.py`

Update the chat endpoint to require authentication:

```python
from typing import Annotated
from ...auth.dependencies import get_current_active_user
from ...models.user import User

@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    # ... existing configuration
)
async def process_chat(
    user_id: str = Path(...),
    request: ChatRequest = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,  # ← Add this
) -> ChatResponse:
    """Process chat with authentication."""

    # Verify user_id matches authenticated user
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's conversations",
        )

    # Rest of your existing code...
```

---

## Phase 2: Frontend Implementation

### Step 11: Install Frontend Dependencies

```bash
cd frontend
npm install react-router-dom jwt-decode zod
npm install --save-dev @types/jwt-decode
```

---

### Step 12: Create Auth Context

**File**: `frontend/src/context/AuthContext.tsx`

```typescript
import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiClient } from '../services/api';
import jwtDecode from 'jwt-decode';

interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

interface TokenPayload {
  user_id: string;
  email: string;
  exp: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  signout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded: TokenPayload = jwtDecode(token);
        // Check if token is expired
        if (decoded.exp * 1000 > Date.now()) {
          // Token valid, fetch user info
          fetchCurrentUser();
        } else {
          // Token expired, try to refresh
          refreshToken();
        }
      } catch (error) {
        console.error('Invalid token:', error);
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.getCurrentUser();
      setUser(response);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      signout();
    }
  };

  const signin = async (email: string, password: string) => {
    try {
      const response = await apiClient.signin(email, password);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setUser(response.user);
    } catch (error) {
      console.error('Signin failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string, fullName: string) => {
    try {
      const response = await apiClient.signup(email, password, fullName);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setUser(response.user);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const signout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        signout();
        return;
      }

      const response = await apiClient.refreshToken(refreshToken);
      localStorage.setItem('access_token', response.access_token);
      await fetchCurrentUser();
    } catch (error) {
      console.error('Token refresh failed:', error);
      signout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        signin,
        signup,
        signout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

---

### Step 13: Update API Client with Auth Methods

**File**: `frontend/src/services/api.ts`

Add these methods to your `ApiClient` class:

```typescript
// Add to ApiClient class

/**
 * User signup
 */
async signup(email: string, password: string, fullName: string): Promise<any> {
  try {
    const response = await this.client.post('/auth/signup', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  } catch (error) {
    this.handleError(error);
    throw error;
  }
}

/**
 * User signin
 */
async signin(email: string, password: string): Promise<any> {
  try {
    const response = await this.client.post('/auth/signin', {
      email,
      password,
    });
    return response.data;
  } catch (error) {
    this.handleError(error);
    throw error;
  }
}

/**
 * Refresh access token
 */
async refreshToken(refreshToken: string): Promise<any> {
  try {
    const response = await this.client.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  } catch (error) {
    this.handleError(error);
    throw error;
  }
}

/**
 * Get current user
 */
async getCurrentUser(): Promise<any> {
  try {
    const response = await this.client.get('/auth/me');
    return response.data;
  } catch (error) {
    this.handleError(error);
    throw error;
  }
}

// Add request interceptor to include token
constructor() {
  this.client = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      "Content-Type": "application/json",
    },
  });

  // Add token to requests
  this.client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Existing interceptors...
}
```

---

### Step 14: Create Signup Page

**File**: `frontend/src/pages/SignupPage.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function SignupPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setIsLoading(true);

    try {
      await signup(email, password, fullName);
      navigate('/'); // Redirect to chat page
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/signin" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign in
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="full-name" className="sr-only">Full name</label>
              <input
                id="full-name"
                name="fullName"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Full name"
              />
            </div>
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password (min 8 characters)"
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="sr-only">Confirm password</label>
              <input
                id="confirm-password"
                name="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Confirm password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

### Step 15: Create Signin Page

**File**: `frontend/src/pages/SigninPage.tsx`

```typescript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function SigninPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { signin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await signin(email, password);
      navigate('/'); // Redirect to chat page
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/signup" className="font-medium text-indigo-600 hover:text-indigo-500">
              Sign up
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

---

### Step 16: Create Protected Route Component

**File**: `frontend/src/components/ProtectedRoute.tsx`

```typescript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/signin" replace />;
  }

  return <>{children}</>;
}
```

---

### Step 17: Setup React Router

**File**: `frontend/src/main.tsx`

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { SignupPage } from './pages/SignupPage';
import { SigninPage } from './pages/SigninPage';
import { SmartTodoApp } from './pages/SmartTodoApp';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/signin" element={<SigninPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <SmartTodoApp />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
```

---

### Step 18: Update SmartTodoApp to Use Auth

**File**: `frontend/src/pages/SmartTodoApp.tsx`

Add logout button and use authenticated user:

```typescript
import { useAuth } from '../context/AuthContext';

export function SmartTodoApp() {
  const { user, signout } = useAuth();

  return (
    <div className="app">
      <header className="app-header">
        <h1>Smart Todo ChatKit</h1>
        <div className="user-info">
          <span>Welcome, {user?.full_name || user?.email}</span>
          <button onClick={signout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>
      {/* Rest of your chat UI */}
    </div>
  );
}
```

---

## Phase 3: Testing

### Step 19: Test Backend APIs

```bash
# Test signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "full_name": "Test User"
  }'

# Test signin
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# Test protected endpoint (replace TOKEN with actual token from signin)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

---

### Step 20: Test Frontend Flow

1. **Start servers**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn src.api.app:app --reload --port 8000

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. **Test flow**:
   - Visit http://localhost:5173
   - Should redirect to `/signin`
   - Click "Sign up" link
   - Create account with email/password
   - Should redirect to chat page
   - Verify user name shows in header
   - Test chat functionality
   - Logout and verify redirect to signin

---

## Summary Checklist

### Backend ✅
- [ ] Install dependencies (python-jose, passlib, etc.)
- [ ] Add JWT env variables (.env)
- [ ] Create User model
- [ ] Run database migration (alembic)
- [ ] Create JWT utilities (jwt.py)
- [ ] Create auth dependencies (dependencies.py)
- [ ] Create auth schemas (schemas.py)
- [ ] Create auth routes (auth.py)
- [ ] Register auth routes in app.py
- [ ] Protect chat route with authentication
- [ ] Test APIs with curl

### Frontend ✅
- [ ] Install dependencies (react-router-dom, jwt-decode)
- [ ] Create AuthContext
- [ ] Update API client with auth methods
- [ ] Create SignupPage component
- [ ] Create SigninPage component
- [ ] Create ProtectedRoute component
- [ ] Setup React Router in main.tsx
- [ ] Update SmartTodoApp with logout
- [ ] Test complete auth flow

---

## Next Steps

After completing these steps:
1. Add password reset functionality
2. Add email verification
3. Implement OAuth providers (Google, GitHub)
4. Add rate limiting to auth endpoints
5. Implement refresh token rotation
6. Add audit logging for security events

---

## Production Deployment

Before deploying to production:

1. **Backend**:
   - Use strong, random JWT secret keys (32+ characters)
   - Enable HTTPS only
   - Set CORS allowed origins to your production domain
   - Use httpOnly cookies instead of localStorage for tokens
   - Implement rate limiting on auth endpoints
   - Add monitoring and alerting

2. **Frontend**:
   - Update `VITE_API_URL` to production backend URL
   - Enable secure, httpOnly cookies
   - Add error tracking (Sentry, etc.)
   - Test on multiple browsers/devices

3. **Database**:
   - Ensure PostgreSQL has strong passwords
   - Enable SSL connections
   - Regular backups
   - Monitor for unusual activity
