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
