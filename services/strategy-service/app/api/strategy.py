"""
Strategy API Endpoints

API endpoints for content strategy generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import logging

from ..models.strategy import (
    StrategyRequest,
    ContentStrategy,
    StrategyAnalysis
)
from ..services.strategy_generator import StrategyGenerator
from ..core.config import get_settings


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/strategy", tags=["Strategy"])


# Dependency to get strategy generator
def get_strategy_generator() -> StrategyGenerator:
    """Get strategy generator instance."""
    settings = get_settings()
    return StrategyGenerator(settings.OPENAI_API_KEY)


@router.post("/generate", response_model=ContentStrategy)
async def generate_strategy(
    request: StrategyRequest,
    generator: StrategyGenerator = Depends(get_strategy_generator)
):
    """
    Generate a comprehensive content strategy.
    
    This endpoint analyzes your industry, target audience, and topics to create
    a complete 90-day content strategy with:
    - Keyword research and clustering
    - 90 article ideas with SEO optimization
    - Weekly publishing schedule
    - Traffic growth projections
    - Strategic recommendations
    
    **Example Request:**
    ```json
    {
      "industry": "technology",
      "target_audience": "Software developers and tech enthusiasts",
      "main_topics": ["AI", "Web Development", "Cloud Computing"],
      "publishing_frequency": "three_times_week",
      "language": "ar",
      "duration_days": 90
    }
    ```
    
    **Response:** Complete content strategy with all details.
    
    **Processing Time:** 30-60 seconds (uses GPT-4 for analysis)
    """
    try:
        logger.info(f"Generating strategy for industry: {request.industry}")
        
        strategy = await generator.generate_strategy(request)
        
        logger.info(f"Strategy generated successfully: {strategy.strategy_id}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"Error generating strategy: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate strategy: {str(e)}"
        )


@router.post("/quick-ideas", response_model=List[dict])
async def generate_quick_ideas(
    topic: str,
    count: int = 10,
    language: str = "ar",
    generator: StrategyGenerator = Depends(get_strategy_generator)
):
    """
    Generate quick article ideas for a single topic.
    
    Faster endpoint for getting article ideas without full strategy.
    
    **Parameters:**
    - **topic**: Main topic or keyword
    - **count**: Number of ideas to generate (1-50)
    - **language**: Content language (ar, en, etc.)
    
    **Example:**
    ```
    POST /api/strategy/quick-ideas?topic=artificial intelligence&count=10&language=ar
    ```
    
    **Response:** List of article ideas with titles and descriptions.
    """
    try:
        if count < 1 or count > 50:
            raise HTTPException(
                status_code=400,
                detail="Count must be between 1 and 50"
            )
        
        # Create a minimal request
        from ..models.strategy import IndustryType, PublishingFrequency
        
        request = StrategyRequest(
            industry=IndustryType.OTHER,
            target_audience="General audience",
            main_topics=[topic],
            publishing_frequency=PublishingFrequency.THREE_TIMES_WEEK,
            language=language,
            duration_days=90
        )
        
        # Generate keyword clusters
        clusters = await generator._generate_keyword_clusters(request)
        
        if not clusters:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate keyword clusters"
            )
        
        # Generate article ideas
        articles = await generator._generate_cluster_articles(
            request,
            clusters[0],
            count
        )
        
        # Convert to simple dict format
        ideas = [
            {
                "title": article.title,
                "description": article.description,
                "content_type": article.content_type.value,
                "keywords": article.keywords,
                "estimated_word_count": article.estimated_word_count,
                "difficulty": article.difficulty,
                "estimated_traffic": article.estimated_traffic,
                "priority": article.priority
            }
            for article in articles
        ]
        
        return ideas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quick ideas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate ideas: {str(e)}"
        )


@router.get("/export/{strategy_id}")
async def export_strategy(strategy_id: str, format: str = "json"):
    """
    Export strategy in different formats.
    
    **Formats:**
    - json: JSON format (default)
    - csv: CSV format for spreadsheet import
    - pdf: PDF report (future)
    
    **Example:**
    ```
    GET /api/strategy/export/abc123?format=csv
    ```
    """
    # TODO: Implement strategy storage and export
    raise HTTPException(
        status_code=501,
        detail="Export functionality coming soon"
    )


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and configuration.
    """
    settings = get_settings()
    
    return {
        "service": "strategy-service",
        "status": "healthy",
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "version": "1.0.0"
    }

