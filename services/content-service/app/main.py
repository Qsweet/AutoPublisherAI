"""
Content Service - Main Application Entry Point

This is the core FastAPI application that handles all content generation requests.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import content

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared'))

try:
    from logging.logger import setup_logging
    from middleware.request_id import RequestIDMiddleware
    logger = setup_logging(
        service_name="content-service",
        log_level=settings.LOG_LEVEL,
        json_format=not settings.DEBUG
    )
    has_middleware = True
except ImportError:
    import logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    has_middleware = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Content Service is starting up...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Content Service is shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="AutoPublisherAI - Content Service",
    description="AI-powered content generation service with advanced SEO optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add Request ID Middleware
if has_middleware:
    app.add_middleware(RequestIDMiddleware)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return {
        "status": "healthy",
        "service": "content-service",
        "version": "1.0.0",
        "environment": settings.APP_ENV
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "AutoPublisherAI - Content Service",
        "version": "1.0.0",
        "description": "AI-powered content generation with SEO optimization",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

