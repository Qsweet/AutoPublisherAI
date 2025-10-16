"""
Publisher Factory

This module implements the Factory Pattern to create publisher instances.
This is a CRITICAL design pattern that makes adding new platforms trivial.
"""

from typing import Dict, Any, Optional
import logging

from app.publishers.base import BasePublisher
from app.publishers.wordpress import WordPressPublisher
from app.publishers.instagram import InstagramPublisher
from app.models.publication import PlatformType

logger = logging.getLogger(__name__)


class PublisherFactory:
    """
    Factory class for creating publisher instances.
    
    This implements the Factory Pattern, which is one of the most
    important design patterns in software engineering.
    
    To add a new platform:
    1. Create a new publisher class (e.g., FacebookPublisher)
    2. Add it to the _publishers dictionary below
    3. That's it! No other code changes needed.
    """
    
    # Registry of available publishers
    _publishers = {
        PlatformType.WORDPRESS: WordPressPublisher,
        PlatformType.INSTAGRAM: InstagramPublisher,
        # Future platforms go here:
        # PlatformType.FACEBOOK: FacebookPublisher,
        # PlatformType.X: XPublisher,
        # PlatformType.LINKEDIN: LinkedInPublisher,
    }
    
    @classmethod
    def create_publisher(
        cls,
        platform: PlatformType,
        config: Dict[str, Any]
    ) -> Optional[BasePublisher]:
        """
        Create a publisher instance for the specified platform.
        
        Args:
            platform: The platform type
            config: Platform-specific configuration
            
        Returns:
            Publisher instance, or None if platform not supported
            
        Raises:
            ValueError: If configuration is invalid
        """
        publisher_class = cls._publishers.get(platform)
        
        if not publisher_class:
            logger.error(f"Publisher not found for platform: {platform}")
            return None
        
        try:
            publisher = publisher_class(config)
            logger.info(f"Created publisher for platform: {platform}")
            return publisher
        except Exception as e:
            logger.error(f"Failed to create publisher for {platform}: {e}")
            raise
    
    @classmethod
    def get_supported_platforms(cls) -> list[PlatformType]:
        """
        Get list of supported platforms.
        
        Returns:
            List of supported platform types
        """
        return list(cls._publishers.keys())
    
    @classmethod
    def is_platform_supported(cls, platform: PlatformType) -> bool:
        """
        Check if a platform is supported.
        
        Args:
            platform: Platform type to check
            
        Returns:
            True if platform is supported
        """
        return platform in cls._publishers


__all__ = [
    "PublisherFactory",
    "BasePublisher",
    "WordPressPublisher",
    "InstagramPublisher"
]

