"""
Authentication Router

API endpoints for user authentication and management.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.auth_service import service
from app.auth_service.schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.auth_service.middleware import get_current_user, get_current_superuser
from app.auth_service.models import User

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ========== PUBLIC ENDPOINTS ==========

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password.",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Creates a new user account with the provided credentials.
    Passwords are securely hashed before storage.

    Args:
        user_data: User registration data (email, username, password, full_name)
        db: Database session

    Returns:
        UserResponse: Created user details (without password)

    Raises:
        HTTPException 400: If username or email already exists
        HTTPException 500: If database error occurs
    """
    try:
        logger.info(f"Attempting to register user: {user_data.username}")
        user = service.create_user(db, user_data)
        return user

    except ValueError as e:
        logger.error(f"Validation error during registration: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with username/email and password to receive JWT tokens.",
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.

    Validates credentials and returns access and refresh tokens.
    Username field accepts either username or email.

    Args:
        login_data: Login credentials (username/email and password)
        db: Database session

    Returns:
        TokenResponse: Access token, refresh token, and expiration info

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 500: If database error occurs
    """
    try:
        logger.info(f"Login attempt for user: {login_data.username}")

        # Authenticate user
        user = service.authenticate_user(db, login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        tokens = service.create_tokens_for_user(user)
        logger.info(f"User logged in successfully: {user.username}")

        return tokens

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh access token",
    description="Use a refresh token to obtain a new access token.",
)
def refresh_token(token_data: RefreshTokenRequest):
    """
    Refresh an access token.

    Use a valid refresh token to obtain a new access token without re-authentication.

    Args:
        token_data: Refresh token request containing the refresh token

    Returns:
        dict: New access token and expiration info

    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    try:
        logger.info("Token refresh attempt")
        new_token = service.refresh_access_token(token_data.refresh_token)
        return new_token

    except ValueError as e:
        logger.error(f"Invalid refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# ========== PROTECTED ENDPOINTS ==========

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's profile.",
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.

    Returns the profile information of the currently authenticated user.

    Args:
        current_user: Current authenticated user (injected by middleware)

    Returns:
        UserResponse: Current user details
    """
    logger.info(f"User profile accessed: {current_user.username}")
    return current_user


@router.get(
    "/health",
    summary="Health check",
    description="Check if the authentication service is running.",
)
def auth_health():
    """
    Health check endpoint.

    Returns:
        dict: Service status
    """
    return {"service": "authentication", "status": "ok"}
