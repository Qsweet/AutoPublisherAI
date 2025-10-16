"""
Auth Service Main Application

FastAPI application for authentication and user management.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'shared'))

from .core.config import get_settings
from .core.database import init_db, close_db
from .api import auth

try:
    from logging.logger import setup_logging
    from middleware.request_id import RequestIDMiddleware
except ImportError:
    # Fallback if shared modules not available
    setup_logging = None
    RequestIDMiddleware = None


settings = get_settings()

# Setup logging
if setup_logging:
    logger = setup_logging(
        service_name="auth-service",
        log_level=settings.LOG_LEVEL if hasattr(settings, 'LOG_LEVEL') else "INFO",
        log_dir=Path("/var/log/autopublisher") if not settings.DEBUG else None,
        json_format=not settings.DEBUG
    )
else:
    import logging
    logger = logging.getLogger("auth-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Auth Service...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Auth Service...")
    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Authentication and user management service for AutoPublisher AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add Request ID Middleware
if RequestIDMiddleware:
    app.add_middleware(RequestIDMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AutoPublisher Auth Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "auth-service"
    }

