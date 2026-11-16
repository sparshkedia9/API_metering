"""
Database setup with SQLAlchemy.

This file creates:
  - engine:       the connection to PostgreSQL (manages a pool of connections)
  - SessionLocal: a factory that creates a new database session
  - Base:         the parent class for all future table models
  - get_db():     a FastAPI dependency that gives each request its own session
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# The engine knows HOW to connect to the database (driver, host, user, etc.).
# pool_pre_ping=True checks that a pooled connection is still alive before using it.
engine = create_engine(settings.database_url, pool_pre_ping=True)

# SessionLocal() creates a new Session object each time it is called.
# autoflush=False: changes are only sent to the DB when we decide to (e.g. commit).
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """All database models (tables) will inherit from this class in later phases."""
    pass


def get_db():
    """
    Provide a database session for a single request, then close it.

    'yield' hands the session to the endpoint. After the endpoint finishes
    (even if it raised an error), the code after 'yield' runs and closes it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
