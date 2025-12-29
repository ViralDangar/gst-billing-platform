"""
Authentication Middleware

FastAPI dependencies for protecting routes with JWT authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.auth_service.models import User
from app.auth_service import service

# HTTPBearer security scheme for extracting tokens from Authorization header
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    This should be used as a dependency in protected route handlers.

    Args:
        credentials: HTTP Bearer credentials containing the JWT token
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException 401: If token is invalid or user not found

    Example:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        user = service.get_current_user_from_token(db, token)
        return user
    except ValueError as e:
        raise credentials_exception
    except Exception as e:
        raise credentials_exception


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current active user.

    Ensures the user account is active.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User: Current active user

    Raises:
        HTTPException 400: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to get the current superuser.

    Ensures the user has superuser privileges.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User: Current superuser

    Raises:
        HTTPException 403: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Dependency to optionally get the current user.

    Returns the user if a valid token is provided, None otherwise.
    Does not raise an exception if no token or invalid token.

    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session

    Returns:
        User or None: Current user if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user = service.get_current_user_from_token(db, token)
        return user
    except:
        return None
