from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.init_db import init_db
from app.db.auto_migrate import ensure_database_compatibility
from app.core.scheduler import app_scheduler
# from app.middleware.compression import CompressionMiddleware
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add compression middleware (temporarily disabled for compatibility)
# app.add_middleware(CompressionMiddleware, minimum_size=1000)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database, upload directories, and scheduler on startup"""
    
    # Auto-migrate database schema to ensure compatibility
    logger.info("🔧 Running database compatibility check...")
    ensure_database_compatibility()
    
    # Initialize database
    init_db()
    
    # Create upload directories
    upload_dir = Path(settings.UPLOAD_FOLDER)
    upload_dir.mkdir(exist_ok=True)
    (upload_dir / "passports").mkdir(exist_ok=True)
    (upload_dir / "agreements").mkdir(exist_ok=True)
    (upload_dir / "videos").mkdir(exist_ok=True)
    
    # Start daily expiration checks
    app_scheduler.start_daily_checks()
    logger.info("🚀 Application startup completed with automated expiration checks")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    app_scheduler.stop()
    logger.info("Application shutdown completed")

@app.get("/")
async def root():
    return {"message": "Nasiya Bro API", "version": settings.VERSION}

@app.get("/scheduler/status")
async def get_scheduler_status():
    """Get information about scheduled jobs"""
    return {
        "status": "active",
        "jobs": app_scheduler.get_jobs(),
        "message": "Automated expiration checks are running"
    } 