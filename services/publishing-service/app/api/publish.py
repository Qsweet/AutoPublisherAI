"""
Publishing API Endpoints

This module defines all REST API endpoints for publishing content.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from app.models.publication import (
    PublicationRequest,
    PublicationResponse,
    BulkPublicationRequest,
    BulkPublicationResponse,
    PlatformStatus,
    PlatformType
)
from app.publishers import PublisherFactory
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/publish",
    response_model=PublicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Publish Content",
    description="Publish content to a single platform"
)
async def publish_content(request: PublicationRequest):
    """
    Publish content to a specified platform.
    
    This endpoint handles publishing to WordPress, Instagram, or any
    other configured platform.
    """
    try:
        logger.info(f"Publishing to {request.platform}")
        
        # Get platform configuration
        config = _get_platform_config(request.platform)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Platform {request.platform} is not configured"
            )
        
        # Create publisher
        publisher = PublisherFactory.create_publisher(request.platform, config)
        
        if not publisher:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create publisher for {request.platform}"
            )
        
        # Publish with retry logic
        response = await publisher.retry_publish(
            request,
            max_attempts=settings.MAX_RETRY_ATTEMPTS,
            delay=settings.RETRY_DELAY_SECONDS
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing content: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish: {str(e)}"
        )


@router.post(
    "/publish/bulk",
    response_model=BulkPublicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk Publish",
    description="Publish content to multiple platforms at once"
)
async def bulk_publish(request: BulkPublicationRequest):
    """
    Publish content to multiple platforms simultaneously.
    
    This is useful when you want to publish the same content
    (or different content) to multiple platforms at once.
    """
    try:
        logger.info(f"Bulk publishing to {len(request.publications)} platforms")
        
        results: List[PublicationResponse] = []
        successful = 0
        failed = 0
        
        for pub_request in request.publications:
            try:
                # Get platform configuration
                config = _get_platform_config(pub_request.platform)
                
                if not config:
                    logger.warning(f"Platform {pub_request.platform} not configured, skipping")
                    continue
                
                # Create publisher
                publisher = PublisherFactory.create_publisher(pub_request.platform, config)
                
                if not publisher:
                    logger.warning(f"Failed to create publisher for {pub_request.platform}, skipping")
                    continue
                
                # Publish
                response = await publisher.retry_publish(pub_request)
                results.append(response)
                
                if response.status.value == "published":
                    successful += 1
                else:
                    failed += 1
                    
                    # Stop on first error if requested
                    if request.stop_on_first_error:
                        logger.info("Stopping bulk publish due to error")
                        break
                
            except Exception as e:
                logger.error(f"Error in bulk publish: {e}")
                failed += 1
                
                if request.stop_on_first_error:
                    break
        
        return BulkPublicationResponse(
            total=len(request.publications),
            successful=successful,
            failed=failed,
            results=results
        )
        
    except Exception as e:
        logger.error(f"Error in bulk publish: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk publish failed: {str(e)}"
        )


@router.get(
    "/platforms",
    response_model=List[PlatformStatus],
    summary="Get Platform Status",
    description="Get the status of all configured platforms"
)
async def get_platform_status():
    """
    Get the status of all publishing platforms.
    
    This checks which platforms are configured and available.
    """
    statuses = []
    
    for platform in PublisherFactory.get_supported_platforms():
        config = _get_platform_config(platform)
        configured = config is not None
        available = False
        error_message = None
        
        if configured:
            try:
                publisher = PublisherFactory.create_publisher(platform, config)
                if publisher:
                    available = await publisher.validate_credentials()
                    if not available:
                        error_message = "Credentials validation failed"
            except Exception as e:
                error_message = str(e)
        else:
            error_message = "Platform not configured"
        
        statuses.append(PlatformStatus(
            platform=platform,
            configured=configured,
            available=available,
            error_message=error_message
        ))
    
    return statuses


@router.delete(
    "/delete/{platform}/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Post",
    description="Delete a post from a platform"
)
async def delete_post(platform: PlatformType, post_id: str):
    """
    Delete a post from a specified platform.
    
    Args:
        platform: The platform type
        post_id: The platform-specific post ID
    """
    try:
        config = _get_platform_config(platform)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Platform {platform} is not configured"
            )
        
        publisher = PublisherFactory.create_publisher(platform, config)
        
        if not publisher:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create publisher for {platform}"
            )
        
        success = await publisher.delete_post(post_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete post {post_id}"
            )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )


def _get_platform_config(platform: PlatformType) -> dict | None:
    """
    Get configuration for a specific platform.
    
    Args:
        platform: Platform type
        
    Returns:
        Configuration dictionary or None if not configured
    """
    if platform == PlatformType.WORDPRESS:
        if settings.wordpress_configured:
            return {
                'url': settings.WORDPRESS_URL,
                'username': settings.WORDPRESS_USERNAME,
                'app_password': settings.WORDPRESS_APP_PASSWORD
            }
    
    elif platform == PlatformType.INSTAGRAM:
        if settings.instagram_configured:
            return {
                'access_token': settings.INSTAGRAM_ACCESS_TOKEN,
                'business_account_id': settings.INSTAGRAM_BUSINESS_ACCOUNT_ID
            }
    
    elif platform == PlatformType.FACEBOOK:
        if settings.facebook_configured:
            return {
                'page_id': settings.FACEBOOK_PAGE_ID,
                'access_token': settings.FACEBOOK_ACCESS_TOKEN
            }
    
    # Add more platforms here as they're implemented
    
    return None


@router.get(
    "/health",
    summary="Service Health Check",
    description="Check if the publishing service is healthy"
)
async def health_check():
    """
    Health check endpoint for the publishing API.
    """
    return {
        "status": "healthy",
        "service": "publishing-api",
        "supported_platforms": [p.value for p in PublisherFactory.get_supported_platforms()],
        "endpoints": {
            "publish": "/api/v1/publish/publish",
            "bulk_publish": "/api/v1/publish/publish/bulk",
            "platforms": "/api/v1/publish/platforms",
            "delete": "/api/v1/publish/delete/{platform}/{post_id}"
        }
    }

