"""
Health-check endpoint.

GET /api/health tells the caller whether the API is running
and whether it can reach the PostgreSQL database.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

# A router groups related endpoints. main.py adds it under the "/api" prefix.
router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # The simplest possible query. If it succeeds, the DB connection works.
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        # The API itself is up, but the database is not reachable.
        # 503 = "Service Unavailable"
        return JSONResponse(
            status_code=503,
            content={"status": "error", "database": "disconnected"},
        )

    # Returning a dict -> FastAPI converts it to JSON with status 200 OK
    return {"status": "ok", "database": "connected"}
