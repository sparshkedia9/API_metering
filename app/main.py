"""
Entry point of the application.

Run the server from the project root with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app import models  # noqa: F401  (imported so all models register with Base)
from app.config import settings
from app.database import Base, engine
from app.routers import auth, health

# Create any tables that don't exist yet (e.g. "users").
# Note: this does NOT modify tables that already exist.
Base.metadata.create_all(bind=engine)

# Create the FastAPI application object
app = FastAPI(title=settings.app_name)

# Register routers. prefix="/api" means the health router's "/health"
# becomes "/api/health".
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
