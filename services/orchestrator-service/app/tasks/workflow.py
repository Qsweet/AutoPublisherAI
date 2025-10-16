"""
Celery Tasks for Workflow Orchestration

This module contains all the background tasks that power the workflow.
These tasks run asynchronously using Celery.
"""

import httpx
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.workflow.generate_and_publish", bind=True)
def generate_and_publish(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main workflow task: Generate content and publish it.
    
    This is the ORCHESTRATOR - it coordinates all the steps.
    
    Args:
        workflow_data: Dictionary containing workflow request data
        
    Returns:
        Dictionary with workflow results
    """
    workflow_id = self.request.id
    logger.info(f"Starting workflow {workflow_id}")
    
    try:
        # Update progress: Starting
        self.update_state(
            state='PROGRESS',
            meta={'progress': 10, 'step': 'Initializing workflow'}
        )
        
        # Step 1: Generate content
        logger.info(f"Workflow {workflow_id}: Generating content...")
        self.update_state(
            state='PROGRESS',
            meta={'progress': 20, 'step': 'Generating content'}
        )
        
        content_result = generate_content_sync(workflow_data['content_params'])
        
        if not content_result or 'error' in content_result:
            raise Exception(f"Content generation failed: {content_result.get('error', 'Unknown error')}")
        
        logger.info(f"Workflow {workflow_id}: Content generated successfully")
        
        # Step 2: Publish to each platform
        if workflow_data.get('auto_publish', True):
            logger.info(f"Workflow {workflow_id}: Publishing to platforms...")
            self.update_state(
                state='PROGRESS',
                meta={'progress': 60, 'step': 'Publishing content'}
            )
            
            publishing_results = []
            
            for target in workflow_data['publishing_targets']:
                try:
                    result = publish_content_sync(content_result, target)
                    publishing_results.append(result)
                except Exception as e:
                    logger.error(f"Failed to publish to {target['platform']}: {e}")
                    publishing_results.append({
                        'platform': target['platform'],
                        'success': False,
                        'error_message': str(e)
                    })
            
            logger.info(f"Workflow {workflow_id}: Publishing completed")
        else:
            publishing_results = []
            logger.info(f"Workflow {workflow_id}: Auto-publish disabled, skipping")
        
        # Step 3: Complete
        self.update_state(
            state='PROGRESS',
            meta={'progress': 100, 'step': 'Workflow completed'}
        )
        
        return {
            'workflow_id': workflow_id,
            'status': 'completed',
            'content': content_result,
            'publishing_results': publishing_results,
            'completed_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {e}", exc_info=True)
        return {
            'workflow_id': workflow_id,
            'status': 'failed',
            'error_message': str(e)
        }


@celery_app.task(name="app.tasks.workflow.generate_content_task")
def generate_content_task(content_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task to generate content using the content service.
    
    Args:
        content_params: Content generation parameters
        
    Returns:
        Generated content data
    """
    return generate_content_sync(content_params)


@celery_app.task(name="app.tasks.workflow.publish_content_task")
def publish_content_task(content: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task to publish content to a platform.
    
    Args:
        content: Generated content
        target: Publishing target configuration
        
    Returns:
        Publishing result
    """
    return publish_content_sync(content, target)


def generate_content_sync(content_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous function to call the content service.
    
    This is separated from the Celery task for easier testing.
    
    Args:
        content_params: Content generation parameters
        
    Returns:
        Generated content data
    """
    try:
        url = f"{settings.CONTENT_SERVICE_URL}/api/v1/content/generate"
        
        with httpx.Client(timeout=300.0) as client:
            response = client.post(url, json=content_params)
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Content service error: {e.response.status_code} - {e.response.text}")
        return {'error': f"HTTP {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        return {'error': str(e)}


def publish_content_sync(content: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous function to call the publishing service.
    
    Args:
        content: Generated content
        target: Publishing target configuration
        
    Returns:
        Publishing result
    """
    try:
        platform = target['platform']
        
        # Build publishing request based on platform
        if platform == 'wordpress':
            publish_data = {
                'platform': 'wordpress',
                'wordpress_data': {
                    'title': content.get('title', ''),
                    'content': _convert_to_html(content),
                    'status': target.get('post_status', 'publish'),
                    'categories': target.get('categories', []),
                    'tags': target.get('tags', []),
                    'featured_image_url': content.get('featured_image', {}).get('url'),
                    'slug': content.get('metadata', {}).get('slug'),
                    'meta_description': content.get('metadata', {}).get('meta_description')
                }
            }
        
        elif platform == 'instagram':
            publish_data = {
                'platform': 'instagram',
                'instagram_data': {
                    'caption': _create_instagram_caption(content),
                    'image_url': content.get('featured_image', {}).get('url', ''),
                    'hashtags': target.get('hashtags', []),
                    'location_id': target.get('location_id')
                }
            }
        
        else:
            return {
                'platform': platform,
                'success': False,
                'error_message': f"Unsupported platform: {platform}"
            }
        
        # Add scheduling if specified
        if target.get('schedule_time'):
            publish_data['schedule_time'] = target['schedule_time']
        
        # Call publishing service
        url = f"{settings.PUBLISHING_SERVICE_URL}/api/v1/publish/publish"
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=publish_data)
            response.raise_for_status()
            result = response.json()
            
            return {
                'platform': platform,
                'success': result.get('status') == 'published',
                'post_id': result.get('platform_post_id'),
                'post_url': result.get('platform_url'),
                'error_message': result.get('error_message')
            }
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Publishing service error: {e.response.status_code} - {e.response.text}")
        return {
            'platform': target['platform'],
            'success': False,
            'error_message': f"HTTP {e.response.status_code}: {e.response.text}"
        }
    except Exception as e:
        logger.error(f"Failed to publish: {e}")
        return {
            'platform': target['platform'],
            'success': False,
            'error_message': str(e)
        }


def _convert_to_html(content: Dict[str, Any]) -> str:
    """
    Convert structured content to HTML for WordPress.
    
    Args:
        content: Generated content structure
        
    Returns:
        HTML string
    """
    html_parts = []
    
    # Introduction
    if content.get('introduction'):
        html_parts.append(f"<p>{content['introduction']}</p>")
    
    # Sections
    for section in content.get('sections', []):
        heading_level = section.get('heading_level', 2)
        html_parts.append(f"<h{heading_level}>{section['heading']}</h{heading_level}>")
        
        # Convert newlines to paragraphs
        paragraphs = section['content'].split('\n\n')
        for para in paragraphs:
            if para.strip():
                html_parts.append(f"<p>{para.strip()}</p>")
    
    # FAQ
    if content.get('faq'):
        html_parts.append("<h2>الأسئلة الشائعة</h2>")
        for faq_item in content['faq']:
            html_parts.append(f"<h3>{faq_item['question']}</h3>")
            html_parts.append(f"<p>{faq_item['answer']}</p>")
    
    # Conclusion
    if content.get('conclusion'):
        html_parts.append(f"<p>{content['conclusion']}</p>")
    
    return '\n'.join(html_parts)


def _create_instagram_caption(content: Dict[str, Any]) -> str:
    """
    Create an Instagram caption from content.
    
    Args:
        content: Generated content
        
    Returns:
        Instagram caption (max 2200 chars)
    """
    title = content.get('title', '')
    intro = content.get('introduction', '')
    
    # Create a concise caption
    caption = f"{title}\n\n{intro}"
    
    # Truncate if too long (leaving room for hashtags)
    if len(caption) > 1800:
        caption = caption[:1797] + "..."
    
    return caption


@celery_app.task(name="app.tasks.workflow.cleanup_old_tasks")
def cleanup_old_tasks():
    """
    Periodic task to clean up old completed tasks.
    
    This runs daily to keep the system clean.
    """
    logger.info("Running cleanup of old tasks...")
    
    # In a real implementation, this would clean up:
    # - Old task results from Redis
    # - Old workflow records from database
    # - Temporary files
    
    # For now, just log
    logger.info("Cleanup completed")
    
    return {"status": "completed", "cleaned": 0}

