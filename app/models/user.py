"""
The User database model.

This class describes the "users" table in PostgreSQL.
Each User object represents one row in that table.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    # The actual table name in PostgreSQL
    __tablename__ = "users"

    # Primary key: a unique number for every user, generated automatically
    id: Mapped[int] = mapped_column(primary_key=True)

    # unique=True -> the database rejects two users with the same email
    # index=True  -> fast lookups by email (login searches by email)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # We NEVER store the plain password, only its hash
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Lets us disable an account without deleting it
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # server_default=func.now() -> PostgreSQL fills in the current time on INSERT
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
