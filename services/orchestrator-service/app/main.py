"""
Orchestrator Service - Main Application Entry Point

This service orchestrates the entire content generation and publishing workflow.
It's the brain of the AutoPublisherAI system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared'))

try:
    from middleware.request_id import RequestIDMiddleware
    has_middleware = True
except ImportError:
    has_middleware = False
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import workflow

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
    logger.info("🚀 Orchestrator Service is starting up...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Content Service URL: {settings.CONTENT_SERVICE_URL}")
    logger.info(f"Publishing Service URL: {settings.PUBLISHING_SERVICE_URL}")
    
    # Test service connections
    logger.info("Testing service connections...")
    
    try:
        import httpx
        
        # Test content service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{settings.CONTENT_SERVICE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Content service is reachable")
                else:
                    logger.warning(f"⚠️  Content service returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️  Cannot reach content service: {e}")
            
            # Test publishing service
            try:
                response = await client.get(f"{settings.PUBLISHING_SERVICE_URL}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info("✅ Publishing service is reachable")
                else:
                    logger.warning(f"⚠️  Publishing service returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️  Cannot reach publishing service: {e}")
    
    except Exception as e:
        logger.error(f"Error testing service connections: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Orchestrator Service is shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="AutoPublisherAI - Orchestrator Service",
    description="Workflow orchestration service for automated content generation and publishing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
# Add Request ID Middleware
if has_middleware:
    app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
        allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ],,  # In production, replace with specific origins
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
        "service": "orchestrator-service",
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
        "service": "AutoPublisherAI - Orchestrator Service",
        "version": "1.0.0",
        "description": "Workflow orchestration for automated content generation and publishing",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "Content generation orchestration",
            "Multi-platform publishing",
            "Background task processing with Celery",
            "Workflow status tracking",
            "Bulk operations support"
        ]
    }


# Include routers
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["Workflow"])


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

