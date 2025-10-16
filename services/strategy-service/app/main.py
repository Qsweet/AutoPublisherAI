"""
Strategy Service - Main Application

FastAPI application for content strategy generation and planning.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .api import strategy


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="AutoPublisher Strategy Service",
    description="""
    # Content Strategy AI Service
    
    This service provides AI-powered content strategy generation for AutoPublisher.
    
    ## Features
    
    - **Comprehensive Strategy Generation**: 90-day content plans with keyword research
    - **SEO Optimization**: Keyword clustering and difficulty analysis
    - **Traffic Projections**: Estimate growth and performance
    - **Article Ideas**: AI-generated article titles and descriptions
    - **Publishing Schedule**: Optimized weekly content calendar
    
    ## How It Works
    
    1. Provide your industry, target audience, and main topics
    2. AI analyzes market and generates keyword clusters
    3. Creates 90 article ideas optimized for SEO
    4. Organizes into weekly publishing schedule
    5. Projects traffic growth over time
    
    ## Powered By
    
    - GPT-4 for content analysis and generation
    - Advanced SEO algorithms
    - Traffic projection models
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategy.router)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Verify OpenAI API key
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set!")
    else:
        logger.info("OpenAI API key configured")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AutoPublisher Strategy Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and configuration.
    """
    return {
        "service": "strategy-service",
        "status": "healthy",
        "environment": settings.APP_ENV,
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

