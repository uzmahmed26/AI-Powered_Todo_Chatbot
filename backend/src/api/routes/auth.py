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


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
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
    result = await session.execute(select(User).where(User.email == user_data.email))
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
    result = await session.execute(select(User).where(User.email == credentials.email))
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
    result = await session.execute(select(User).where(User.id == token_data.user_id))
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
async def signout(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Sign out current user (client should delete tokens).

    Note: Since JWT is stateless, actual logout happens on client side.
    This endpoint is for consistency and future token blacklisting.
    """
    logger.info(f"User signed out: {current_user.email}")
    return None
