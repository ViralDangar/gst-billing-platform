"""
Authentication Service

Business logic for user authentication and management.
"""

import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.auth_service.models import User
from app.auth_service.schemas import UserCreate, TokenData
from app.auth_service.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

# Configure logging
logger = logging.getLogger(__name__)


# ========== USER OPERATIONS ==========

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user with hashed password.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        User: Created user object

    Raises:
        ValueError: If username or email already exists
    """
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise ValueError("Username already registered")

        # Check if email already exists
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise ValueError("Email already registered")

        # Create new user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created successfully: {user.username}")
        return user

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating user: {str(e)}")
        raise ValueError("Username or email already exists")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get user by username.

    Args:
        db: Database session
        username: Username to search for

    Returns:
        User or None: User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email.

    Args:
        db: Database session
        email: Email to search for

    Returns:
        User or None: User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        User or None: User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


# ========== AUTHENTICATION OPERATIONS ==========

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username/email and password.

    Args:
        db: Database session
        username: Username or email
        password: Plain text password

    Returns:
        User or None: User object if authentication successful, None otherwise
    """
    # Try to find user by username first
    user = get_user_by_username(db, username)

    # If not found, try email
    if not user:
        user = get_user_by_email(db, username)

    # Verify password
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Failed authentication attempt for: {username}")
        return None

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user login attempt: {username}")
        return None

    logger.info(f"User authenticated successfully: {user.username}")
    return user


def create_tokens_for_user(user: User) -> dict:
    """
    Create access and refresh tokens for a user.

    Args:
        user: User object

    Returns:
        dict: Dictionary containing access_token, refresh_token, token_type, and expires_in
    """
    token_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
    }


def refresh_access_token(refresh_token: str) -> dict:
    """
    Create a new access token from a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        dict: Dictionary containing new access_token and token info

    Raises:
        ValueError: If refresh token is invalid or expired
    """
    try:
        payload = decode_token(refresh_token)

        # Verify it's a refresh token
        if not verify_token_type(payload, "refresh"):
            raise ValueError("Invalid token type")

        # Create new access token with same data
        token_data = {
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "is_superuser": payload.get("is_superuser"),
        }

        access_token = create_access_token(token_data)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise ValueError("Invalid or expired refresh token")


def get_current_user_from_token(db: Session, token: str) -> User:
    """
    Get current user from access token.

    Args:
        db: Database session
        token: JWT access token

    Returns:
        User: User object

    Raises:
        ValueError: If token is invalid or user not found
    """
    try:
        payload = decode_token(token)

        # Verify it's an access token
        if not verify_token_type(payload, "access"):
            raise ValueError("Invalid token type")

        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = get_user_by_id(db, uuid.UUID(user_id))
        if not user:
            raise ValueError("User not found")

        if not user.is_active:
            raise ValueError("User is inactive")

        return user

    except Exception as e:
        logger.error(f"Error getting user from token: {str(e)}")
        raise ValueError("Could not validate credentials")
