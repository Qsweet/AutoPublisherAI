"""
WordPress Publisher

Handles publishing content to WordPress sites via REST API.

This uses WordPress Application Passwords for secure authentication.
"""

import httpx
import base64
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

from app.publishers.base import BasePublisher
from app.models.publication import (
    PublicationRequest,
    PublicationResponse,
    PublicationStatus,
    PlatformType,
    WordPressPostData
)


class WordPressPublisher(BasePublisher):
    """
    WordPress publisher using REST API v2.
    
    This implements the official WordPress REST API specification
    for maximum compatibility.
    """
    
    @property
    def platform_type(self) -> PlatformType:
        """Return WordPress platform type."""
        return PlatformType.WORDPRESS
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize WordPress publisher.
        
        Args:
            config: Must contain 'url', 'username', and 'app_password'
        """
        super().__init__(config)
        
        self.site_url = config.get('url', '').rstrip('/')
        self.username = config.get('username')
        self.app_password = config.get('app_password')
        
        # Validate configuration
        if not all([self.site_url, self.username, self.app_password]):
            raise ValueError("WordPress configuration incomplete. Need: url, username, app_password")
        
        # Create authentication header
        credentials = f"{self.username}:{self.app_password}"
        token = base64.b64encode(credentials.encode()).decode()
        self.auth_header = f"Basic {token}"
        
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
    
    async def publish(self, request: PublicationRequest) -> PublicationResponse:
        """
        Publish a post to WordPress.
        
        Args:
            request: Publication request with WordPress data
            
        Returns:
            PublicationResponse with WordPress post details
        """
        if not request.wordpress_data:
            raise ValueError("WordPress data is required for WordPress publishing")
        
        wp_data = request.wordpress_data
        publication_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Publishing to WordPress: {wp_data.title}")
            
            # Step 1: Upload featured image (if provided)
            featured_media_id = None
            if wp_data.featured_image_url:
                featured_media_id = await self._upload_image(wp_data.featured_image_url)
            
            # Step 2: Get or create categories
            category_ids = []
            if wp_data.categories:
                category_ids = await self._get_or_create_categories(wp_data.categories)
            
            # Step 3: Get or create tags
            tag_ids = []
            if wp_data.tags:
                tag_ids = await self._get_or_create_tags(wp_data.tags)
            
            # Step 4: Create the post
            post_data = {
                "title": wp_data.title,
                "content": wp_data.content,
                "status": wp_data.status,
                "excerpt": wp_data.excerpt or "",
            }
            
            if wp_data.slug:
                post_data["slug"] = wp_data.slug
            
            if featured_media_id:
                post_data["featured_media"] = featured_media_id
            
            if category_ids:
                post_data["categories"] = category_ids
            
            if tag_ids:
                post_data["tags"] = tag_ids
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/posts",
                    json=post_data,
                    headers={
                        "Authorization": self.auth_header,
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
            
            # Extract response data
            post_id = str(result.get('id'))
            post_url = result.get('link')
            
            self.logger.info(f"Successfully published to WordPress. Post ID: {post_id}")
            
            return self._create_response(
                publication_id=publication_id,
                status=PublicationStatus.PUBLISHED,
                platform_post_id=post_id,
                platform_url=post_url
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"WordPress API error: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            return self._create_response(
                publication_id=publication_id,
                status=PublicationStatus.FAILED,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._create_response(
                publication_id=publication_id,
                status=PublicationStatus.FAILED,
                error_message=error_msg
            )
    
    async def _upload_image(self, image_url: str) -> Optional[int]:
        """
        Upload an image to WordPress media library.
        
        Args:
            image_url: URL of the image to upload
            
        Returns:
            Media ID if successful, None otherwise
        """
        try:
            self.logger.info(f"Uploading image from: {image_url}")
            
            # Download the image
            async with httpx.AsyncClient() as client:
                img_response = await client.get(image_url, timeout=30.0)
                img_response.raise_for_status()
                image_data = img_response.content
                
                # Get content type
                content_type = img_response.headers.get('content-type', 'image/jpeg')
                
                # Upload to WordPress
                upload_response = await client.post(
                    f"{self.api_base}/media",
                    content=image_data,
                    headers={
                        "Authorization": self.auth_header,
                        "Content-Type": content_type,
                        "Content-Disposition": 'attachment; filename="featured-image.jpg"'
                    },
                    timeout=60.0
                )
                
                upload_response.raise_for_status()
                result = upload_response.json()
                
                media_id = result.get('id')
                self.logger.info(f"Image uploaded successfully. Media ID: {media_id}")
                return media_id
                
        except Exception as e:
            self.logger.error(f"Failed to upload image: {e}")
            return None
    
    async def _get_or_create_categories(self, category_names: list[str]) -> list[int]:
        """
        Get or create WordPress categories.
        
        Args:
            category_names: List of category names
            
        Returns:
            List of category IDs
        """
        category_ids = []
        
        async with httpx.AsyncClient() as client:
            for name in category_names:
                try:
                    # Search for existing category
                    search_response = await client.get(
                        f"{self.api_base}/categories",
                        params={"search": name},
                        headers={"Authorization": self.auth_header},
                        timeout=10.0
                    )
                    
                    categories = search_response.json()
                    
                    if categories:
                        # Use existing category
                        category_ids.append(categories[0]['id'])
                    else:
                        # Create new category
                        create_response = await client.post(
                            f"{self.api_base}/categories",
                            json={"name": name},
                            headers={
                                "Authorization": self.auth_header,
                                "Content-Type": "application/json"
                            },
                            timeout=10.0
                        )
                        
                        if create_response.status_code == 201:
                            new_category = create_response.json()
                            category_ids.append(new_category['id'])
                            
                except Exception as e:
                    self.logger.warning(f"Failed to process category '{name}': {e}")
        
        return category_ids
    
    async def _get_or_create_tags(self, tag_names: list[str]) -> list[int]:
        """
        Get or create WordPress tags.
        
        Args:
            tag_names: List of tag names
            
        Returns:
            List of tag IDs
        """
        tag_ids = []
        
        async with httpx.AsyncClient() as client:
            for name in tag_names:
                try:
                    # Search for existing tag
                    search_response = await client.get(
                        f"{self.api_base}/tags",
                        params={"search": name},
                        headers={"Authorization": self.auth_header},
                        timeout=10.0
                    )
                    
                    tags = search_response.json()
                    
                    if tags:
                        # Use existing tag
                        tag_ids.append(tags[0]['id'])
                    else:
                        # Create new tag
                        create_response = await client.post(
                            f"{self.api_base}/tags",
                            json={"name": name},
                            headers={
                                "Authorization": self.auth_header,
                                "Content-Type": "application/json"
                            },
                            timeout=10.0
                        )
                        
                        if create_response.status_code == 201:
                            new_tag = create_response.json()
                            tag_ids.append(new_tag['id'])
                            
                except Exception as e:
                    self.logger.warning(f"Failed to process tag '{name}': {e}")
        
        return tag_ids
    
    async def validate_credentials(self) -> bool:
        """
        Validate WordPress credentials.
        
        Returns:
            True if credentials are valid
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base}/users/me",
                    headers={"Authorization": self.auth_header},
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a WordPress post.
        
        Args:
            post_id: WordPress post ID
            
        Returns:
            True if deletion was successful
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.api_base}/posts/{post_id}",
                    headers={"Authorization": self.auth_header},
                    params={"force": True},  # Permanently delete
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Failed to delete post {post_id}: {e}")
            return False

