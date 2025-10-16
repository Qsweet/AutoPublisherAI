"""
Publication Data Models

Pydantic models for publishing requests and responses.
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """Supported publishing platforms."""
    WORDPRESS = "wordpress"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    X = "x"  # Twitter/X
    LINKEDIN = "linkedin"


class PublicationStatus(str, Enum):
    """Publication status."""
    PENDING = "pending"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


class WordPressPostData(BaseModel):
    """Data specific to WordPress posts."""
    title: str = Field(..., description="Post title")
    content: str = Field(..., description="Post content (HTML)")
    excerpt: Optional[str] = Field(None, description="Post excerpt")
    status: str = Field(default="publish", description="Post status (draft, publish, etc.)")
    categories: List[str] = Field(default_factory=list, description="Post categories")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    featured_image_url: Optional[str] = Field(None, description="Featured image URL")
    slug: Optional[str] = Field(None, description="Post slug")
    meta_description: Optional[str] = Field(None, description="SEO meta description")


class InstagramPostData(BaseModel):
    """Data specific to Instagram posts."""
    caption: str = Field(..., max_length=2200, description="Post caption")
    image_url: str = Field(..., description="Image URL to publish")
    location_id: Optional[str] = Field(None, description="Location ID")
    hashtags: List[str] = Field(default_factory=list, max_length=30, description="Hashtags")
    
    @property
    def full_caption(self) -> str:
        """Get caption with hashtags."""
        caption = self.caption
        if self.hashtags:
            hashtag_str = ' '.join([f"#{tag}" for tag in self.hashtags])
            caption = f"{caption}\n\n{hashtag_str}"
        return caption[:2200]  # Instagram limit


class FacebookPostData(BaseModel):
    """Data specific to Facebook posts."""
    message: str = Field(..., description="Post message")
    link: Optional[str] = Field(None, description="Link to share")
    image_url: Optional[str] = Field(None, description="Image URL")
    scheduled_publish_time: Optional[datetime] = Field(None, description="Scheduled time")


class XPostData(BaseModel):
    """Data specific to X (Twitter) posts."""
    text: str = Field(..., max_length=280, description="Tweet text")
    media_urls: List[str] = Field(default_factory=list, max_length=4, description="Media URLs")
    reply_to: Optional[str] = Field(None, description="Tweet ID to reply to")


class PublicationRequest(BaseModel):
    """
    Request to publish content to a platform.
    """
    platform: PlatformType = Field(..., description="Target platform")
    
    # Platform-specific data (only one should be provided)
    wordpress_data: Optional[WordPressPostData] = None
    instagram_data: Optional[InstagramPostData] = None
    facebook_data: Optional[FacebookPostData] = None
    x_data: Optional[XPostData] = None
    
    # Scheduling
    schedule_time: Optional[datetime] = Field(None, description="When to publish (None = immediate)")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform": "wordpress",
                "wordpress_data": {
                    "title": "مقال رائع عن الذكاء الاصطناعي",
                    "content": "<p>محتوى المقال...</p>",
                    "status": "publish",
                    "categories": ["تقنية", "ذكاء اصطناعي"],
                    "tags": ["AI", "تكنولوجيا"]
                }
            }
        }


class PublicationResponse(BaseModel):
    """
    Response after publishing content.
    """
    publication_id: str = Field(..., description="Unique publication ID")
    platform: PlatformType = Field(..., description="Platform published to")
    status: PublicationStatus = Field(..., description="Publication status")
    
    # Platform-specific response data
    platform_post_id: Optional[str] = Field(None, description="ID on the platform")
    platform_url: Optional[str] = Field(None, description="URL of published content")
    
    # Timing
    published_at: Optional[datetime] = Field(None, description="When it was published")
    scheduled_for: Optional[datetime] = Field(None, description="When it's scheduled for")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if failed")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BulkPublicationRequest(BaseModel):
    """
    Request to publish to multiple platforms at once.
    """
    publications: List[PublicationRequest] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of publication requests"
    )
    
    stop_on_first_error: bool = Field(
        default=False,
        description="Whether to stop if one publication fails"
    )


class BulkPublicationResponse(BaseModel):
    """
    Response for bulk publication.
    """
    total: int = Field(..., description="Total publications requested")
    successful: int = Field(..., description="Number of successful publications")
    failed: int = Field(..., description="Number of failed publications")
    results: List[PublicationResponse] = Field(..., description="Individual results")


class PlatformStatus(BaseModel):
    """
    Status of a publishing platform.
    """
    platform: PlatformType
    configured: bool = Field(..., description="Whether platform is configured")
    available: bool = Field(..., description="Whether platform is currently available")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None

