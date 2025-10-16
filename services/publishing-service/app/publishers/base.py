"""
Base Publisher Interface

This defines the contract that all platform publishers must follow.
This is a CRITICAL design pattern that makes the system extensible.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging

from app.models.publication import (
    PublicationRequest,
    PublicationResponse,
    PublicationStatus,
    PlatformType
)

logger = logging.getLogger(__name__)


class BasePublisher(ABC):
    """
    Abstract base class for all platform publishers.
    
    This implements the Strategy Pattern, allowing us to swap
    publishing strategies at runtime.
    
    To add a new platform:
    1. Create a new class that inherits from BasePublisher
    2. Implement the required methods
    3. Register it in the PublisherFactory
    
    That's it! No changes to existing code needed.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the publisher with configuration.
        
        Args:
            config: Platform-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def platform_type(self) -> PlatformType:
        """
        Return the platform type this publisher handles.
        
        This must be implemented by each publisher.
        """
        pass
    
    @abstractmethod
    async def publish(self, request: PublicationRequest) -> PublicationResponse:
        """
        Publish content to the platform.
        
        This is the main method that must be implemented by each publisher.
        
        Args:
            request: Publication request with all necessary data
            
        Returns:
            PublicationResponse with result details
            
        Raises:
            Exception: If publication fails
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that the platform credentials are correct.
        
        This should make a simple API call to verify authentication.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the platform.
        
        Args:
            post_id: Platform-specific post ID
            
        Returns:
            True if deletion was successful
        """
        pass
    
    async def is_available(self) -> bool:
        """
        Check if the platform is currently available.
        
        This can be overridden by publishers to add custom health checks.
        
        Returns:
            True if platform is available
        """
        try:
            return await self.validate_credentials()
        except Exception as e:
            self.logger.error(f"Platform availability check failed: {e}")
            return False
    
    def _create_response(
        self,
        publication_id: str,
        status: PublicationStatus,
        platform_post_id: Optional[str] = None,
        platform_url: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> PublicationResponse:
        """
        Helper method to create a standardized response.
        
        Args:
            publication_id: Unique ID for this publication
            status: Publication status
            platform_post_id: ID on the platform
            platform_url: URL of published content
            error_message: Error message if failed
            
        Returns:
            PublicationResponse object
        """
        return PublicationResponse(
            publication_id=publication_id,
            platform=self.platform_type,
            status=status,
            platform_post_id=platform_post_id,
            platform_url=platform_url,
            error_message=error_message
        )
    
    async def retry_publish(
        self,
        request: PublicationRequest,
        max_attempts: int = 3,
        delay: int = 5
    ) -> PublicationResponse:
        """
        Publish with automatic retry logic.
        
        This implements exponential backoff for failed requests.
        
        Args:
            request: Publication request
            max_attempts: Maximum retry attempts
            delay: Initial delay between retries (seconds)
            
        Returns:
            PublicationResponse
        """
        import asyncio
        
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                self.logger.info(f"Publishing attempt {attempt}/{max_attempts}")
                response = await self.publish(request)
                
                if response.status == PublicationStatus.PUBLISHED:
                    return response
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    f"Attempt {attempt} failed: {e}. "
                    f"Retrying in {delay * attempt} seconds..."
                )
                
                if attempt < max_attempts:
                    await asyncio.sleep(delay * attempt)  # Exponential backoff
        
        # All attempts failed
        return self._create_response(
            publication_id=f"failed_{request.platform.value}",
            status=PublicationStatus.FAILED,
            error_message=f"Failed after {max_attempts} attempts. Last error: {last_error}"
        )

