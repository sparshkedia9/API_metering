"""
Pydantic schemas for users and authentication.

Schemas describe the shape of JSON data that goes IN to the API (requests)
and OUT of the API (responses). They are separate from the SQLAlchemy
models, which describe database tables.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Request body for POST /api/auth/register."""

    email: EmailStr  # must be a valid email address
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Request body for POST /api/auth/login."""

    email: EmailStr
    password: str  # no length rules here: we only check if it matches


class UserResponse(BaseModel):
    """What the API returns about a user. Note: there is NO password field."""

    # Allows building this schema from a SQLAlchemy User object (user.email, ...)
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """Response body for a successful login."""

    access_token: str
    token_type: str = "bearer"
