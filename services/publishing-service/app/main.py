"""
Publishing Service - Main Application Entry Point

This service handles publishing content to various platforms.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import publish

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Publishing Service is starting up...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    
    # Log configured platforms
    platforms = []
    if settings.wordpress_configured:
        platforms.append("WordPress")
    if settings.instagram_configured:
        platforms.append("Instagram")
    if settings.facebook_configured:
        platforms.append("Facebook")
    if settings.x_configured:
        platforms.append("X")
    
    if platforms:
        logger.info(f"Configured platforms: {', '.join(platforms)}")
    else:
        logger.warning("⚠️  No platforms configured yet!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Publishing Service is shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="AutoPublisherAI - Publishing Service",
    description="Multi-platform content publishing service with plugin architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return {
        "status": "healthy",
        "service": "publishing-service",
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
        "service": "AutoPublisherAI - Publishing Service",
        "version": "1.0.0",
        "description": "Multi-platform content publishing with plugin architecture",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(publish.router, prefix="/api/v1/publish", tags=["Publishing"])


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

