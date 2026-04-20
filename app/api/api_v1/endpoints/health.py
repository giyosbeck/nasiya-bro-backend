from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/live")
def liveness():
    """Liveness probe — process is alive."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe — process + DB are healthy."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        return {
            "status": "degraded",
            "database": f"error: {exc.__class__.__name__}",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    return {
        "status": "ok",
        "database": db_status,
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
