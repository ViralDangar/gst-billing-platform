"""
Authentication Schemas

Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from datetime import datetime


# ---------- USER SCHEMAS ----------

class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (without password)."""

    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- AUTHENTICATION SCHEMAS ----------

class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""

    refresh_token: str


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: str
    username: str
    email: str
    is_superuser: bool
