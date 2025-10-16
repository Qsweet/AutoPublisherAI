"""
Instagram Publisher

Handles publishing content to Instagram using the Instagram Graph API.

This requires an Instagram Business Account connected to a Facebook Page.
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
import uuid

from app.publishers.base import BasePublisher
from app.models.publication import (
    PublicationRequest,
    PublicationResponse,
    PublicationStatus,
    PlatformType,
    InstagramPostData
)


class InstagramPublisher(BasePublisher):
    """
    Instagram publisher using Graph API.
    
    This implements the two-step process required by Instagram:
    1. Create a media container
    2. Publish the container
    
    This is the OFFICIAL and SAFE way to post to Instagram programmatically.
    """
    
    @property
    def platform_type(self) -> PlatformType:
        """Return Instagram platform type."""
        return PlatformType.INSTAGRAM
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Instagram publisher.
        
        Args:
            config: Must contain 'access_token' and 'business_account_id'
        """
        super().__init__(config)
        
        self.access_token = config.get('access_token')
        self.business_account_id = config.get('business_account_id')
        
        # Validate configuration
        if not all([self.access_token, self.business_account_id]):
            raise ValueError("Instagram configuration incomplete. Need: access_token, business_account_id")
        
        self.graph_api_base = "https://graph.facebook.com/v18.0"
    
    async def publish(self, request: PublicationRequest) -> PublicationResponse:
        """
        Publish a post to Instagram.
        
        Instagram requires a two-step process:
        1. Create a media container (upload)
        2. Publish the container
        
        Args:
            request: Publication request with Instagram data
            
        Returns:
            PublicationResponse with Instagram post details
        """
        if not request.instagram_data:
            raise ValueError("Instagram data is required for Instagram publishing")
        
        ig_data = request.instagram_data
        publication_id = str(uuid.uuid4())
        
        try:
            self.logger.info(f"Publishing to Instagram: {ig_data.caption[:50]}...")
            
            # Step 1: Create media container
            container_id = await self._create_media_container(ig_data)
            
            if not container_id:
                raise Exception("Failed to create media container")
            
            # Step 2: Wait for container to be ready (Instagram processes the image)
            self.logger.info(f"Waiting for container {container_id} to be ready...")
            await asyncio.sleep(3)  # Give Instagram time to process
            
            # Step 3: Publish the container
            media_id = await self._publish_container(container_id)
            
            if not media_id:
                raise Exception("Failed to publish media container")
            
            # Step 4: Get the post URL
            post_url = f"https://www.instagram.com/p/{await self._get_media_code(media_id)}"
            
            self.logger.info(f"Successfully published to Instagram. Media ID: {media_id}")
            
            return self._create_response(
                publication_id=publication_id,
                status=PublicationStatus.PUBLISHED,
                platform_post_id=media_id,
                platform_url=post_url
            )
            
        except Exception as e:
            error_msg = f"Instagram publishing error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._create_response(
                publication_id=publication_id,
                status=PublicationStatus.FAILED,
                error_message=error_msg
            )
    
    async def _create_media_container(self, ig_data: InstagramPostData) -> Optional[str]:
        """
        Create an Instagram media container.
        
        This is step 1 of the Instagram publishing process.
        
        Args:
            ig_data: Instagram post data
            
        Returns:
            Container ID if successful, None otherwise
        """
        try:
            endpoint = f"{self.graph_api_base}/{self.business_account_id}/media"
            
            params = {
                "image_url": ig_data.image_url,
                "caption": ig_data.full_caption,
                "access_token": self.access_token
            }
            
            # Add location if provided
            if ig_data.location_id:
                params["location_id"] = ig_data.location_id
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    params=params,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                container_id = result.get('id')
                self.logger.info(f"Media container created: {container_id}")
                return container_id
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to create container: {e.response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating container: {e}")
            return None
    
    async def _publish_container(self, container_id: str) -> Optional[str]:
        """
        Publish an Instagram media container.
        
        This is step 2 of the Instagram publishing process.
        
        Args:
            container_id: The container ID from step 1
            
        Returns:
            Media ID if successful, None otherwise
        """
        try:
            endpoint = f"{self.graph_api_base}/{self.business_account_id}/media_publish"
            
            params = {
                "creation_id": container_id,
                "access_token": self.access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint,
                    params=params,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                media_id = result.get('id')
                self.logger.info(f"Media published: {media_id}")
                return media_id
                
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Failed to publish container: {e.response.text}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error publishing container: {e}")
            return None
    
    async def _get_media_code(self, media_id: str) -> str:
        """
        Get the Instagram media code (shortcode) for a media ID.
        
        This is used to construct the Instagram post URL.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Media code/shortcode
        """
        try:
            endpoint = f"{self.graph_api_base}/{media_id}"
            
            params = {
                "fields": "shortcode",
                "access_token": self.access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params=params,
                    timeout=10.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                return result.get('shortcode', media_id)
                
        except Exception as e:
            self.logger.error(f"Failed to get media code: {e}")
            return media_id  # Fallback to media ID
    
    async def validate_credentials(self) -> bool:
        """
        Validate Instagram credentials.
        
        Returns:
            True if credentials are valid
        """
        try:
            endpoint = f"{self.graph_api_base}/{self.business_account_id}"
            
            params = {
                "fields": "id,username",
                "access_token": self.access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    username = result.get('username', 'Unknown')
                    self.logger.info(f"Instagram credentials valid. Account: @{username}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Credential validation failed: {e}")
            return False
    
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete an Instagram post.
        
        Note: Instagram Graph API has limitations on deleting posts.
        This may not work for all post types.
        
        Args:
            post_id: Instagram media ID
            
        Returns:
            True if deletion was successful
        """
        try:
            endpoint = f"{self.graph_api_base}/{post_id}"
            
            params = {
                "access_token": self.access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    endpoint,
                    params=params,
                    timeout=10.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Failed to delete post {post_id}: {e}")
            return False
    
    async def get_account_insights(self) -> Dict[str, Any]:
        """
        Get Instagram account insights (analytics).
        
        This is a BONUS feature for monitoring performance.
        
        Returns:
            Dictionary with account insights
        """
        try:
            endpoint = f"{self.graph_api_base}/{self.business_account_id}/insights"
            
            params = {
                "metric": "impressions,reach,profile_views",
                "period": "day",
                "access_token": self.access_token
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                
                return {}
                
        except Exception as e:
            self.logger.error(f"Failed to get insights: {e}")
            return {}

