"""
Content API Endpoints

This module defines all REST API endpoints for content generation.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
import logging
import uuid
from typing import Dict

from app.models.article import (
    ArticleGenerationRequest,
    ArticleGenerationResponse,
    ArticleGenerationStatus
)
from app.services.content_generator import ContentGenerator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Initialize content generator
content_generator = ContentGenerator()

# In-memory task storage (in production, use Redis or database)
tasks: Dict[str, ArticleGenerationStatus] = {}


@router.post(
    "/generate",
    response_model=ArticleGenerationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Article (Synchronous)",
    description="Generate a complete SEO-optimized article synchronously. This may take 30-60 seconds."
)
async def generate_article(request: ArticleGenerationRequest):
    """
    Generate a complete article synchronously.
    
    This endpoint will wait until the article is fully generated before returning.
    Use this for immediate results, but be aware it may take time.
    
    **Note:** For better user experience, consider using the async endpoint `/generate-async`.
    """
    try:
        logger.info(f"Received article generation request: {request.topic}")
        
        # Generate article
        article = await content_generator.generate_article(request)
        
        logger.info(f"Article generated successfully: {article.title}")
        return article
        
    except Exception as e:
        logger.error(f"Error generating article: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate article: {str(e)}"
        )


@router.post(
    "/generate-async",
    response_model=ArticleGenerationStatus,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Article (Asynchronous)",
    description="Start article generation as a background task. Returns immediately with a task ID."
)
async def generate_article_async(
    request: ArticleGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate an article asynchronously.
    
    This endpoint returns immediately with a task ID. You can then poll
    the `/status/{task_id}` endpoint to check progress and get results.
    
    This is the RECOMMENDED approach for production applications.
    """
    try:
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Create initial task status
        task_status = ArticleGenerationStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            message="Task queued for processing"
        )
        
        # Store task
        tasks[task_id] = task_status
        
        # Add to background tasks
        background_tasks.add_task(
            _generate_article_background,
            task_id,
            request
        )
        
        logger.info(f"Article generation task created: {task_id}")
        return task_status
        
    except Exception as e:
        logger.error(f"Error creating background task: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get(
    "/status/{task_id}",
    response_model=ArticleGenerationStatus,
    summary="Check Task Status",
    description="Check the status of an asynchronous article generation task."
)
async def get_task_status(task_id: str):
    """
    Get the status of an article generation task.
    
    Returns the current status, progress, and result (if completed).
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return tasks[task_id]


@router.delete(
    "/status/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Delete a completed or failed task from memory."
)
async def delete_task(task_id: str):
    """
    Delete a task from the task storage.
    
    Use this to clean up completed or failed tasks.
    """
    if task_id not in tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    del tasks[task_id]
    logger.info(f"Task deleted: {task_id}")
    return None


@router.get(
    "/tasks",
    response_model=list[ArticleGenerationStatus],
    summary="List All Tasks",
    description="Get a list of all tasks (pending, processing, completed, failed)."
)
async def list_tasks():
    """
    List all tasks in the system.
    
    Useful for monitoring and debugging.
    """
    return list(tasks.values())


# Background task function
async def _generate_article_background(task_id: str, request: ArticleGenerationRequest):
    """
    Background task for article generation.
    
    This runs in the background and updates the task status as it progresses.
    """
    try:
        # Update status: processing
        tasks[task_id].status = "processing"
        tasks[task_id].progress = 10
        tasks[task_id].message = "Starting article generation..."
        
        # Generate article
        logger.info(f"Background task {task_id}: Starting generation")
        
        tasks[task_id].progress = 30
        tasks[task_id].message = "Analyzing SEO and keywords..."
        
        article = await content_generator.generate_article(request)
        
        # Update status: completed
        tasks[task_id].status = "completed"
        tasks[task_id].progress = 100
        tasks[task_id].message = "Article generated successfully"
        tasks[task_id].result = article
        
        logger.info(f"Background task {task_id}: Completed successfully")
        
    except Exception as e:
        # Update status: failed
        tasks[task_id].status = "failed"
        tasks[task_id].progress = 0
        tasks[task_id].message = "Article generation failed"
        tasks[task_id].error = str(e)
        
        logger.error(f"Background task {task_id}: Failed with error: {e}", exc_info=True)


@router.get(
    "/health",
    summary="Service Health Check",
    description="Check if the content generation service is healthy and ready."
)
async def health_check():
    """
    Health check endpoint for the content API.
    """
    return {
        "status": "healthy",
        "service": "content-api",
        "endpoints": {
            "generate": "/api/v1/content/generate",
            "generate_async": "/api/v1/content/generate-async",
            "status": "/api/v1/content/status/{task_id}",
            "tasks": "/api/v1/content/tasks"
        }
    }

