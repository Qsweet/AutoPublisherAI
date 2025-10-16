"""
Workflow API Endpoints

This is the main API that users interact with.
It provides a simple interface to the complex orchestration behind the scenes.
"""

from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from celery.result import AsyncResult
from typing import List
import logging
import uuid

from app.models.workflow import (
    WorkflowRequest,
    WorkflowResponse,
    WorkflowStatus,
    BulkWorkflowRequest,
    BulkWorkflowResponse
)
from app.tasks.workflow import generate_and_publish
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post(
    "/execute",
    response_model=WorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute Workflow",
    description="Start a complete content generation and publishing workflow"
)
async def execute_workflow(request: WorkflowRequest):
    """
    Execute a complete workflow: generate content and publish it.
    
    This is the MAIN ENDPOINT that users will use.
    It's simple on the surface but powerful underneath.
    
    Example:
        POST /api/v1/workflow/execute
        {
            "content_params": {
                "topic": "فوائد العمل عن بعد",
                "language": "ar",
                "target_length": 1500
            },
            "publishing_targets": [
                {"platform": "wordpress"},
                {"platform": "instagram"}
            ]
        }
    """
    try:
        logger.info(f"Executing workflow for topic: {request.content_params.topic}")
        
        # Convert request to dict for Celery
        workflow_data = {
            'content_params': request.content_params.model_dump(),
            'publishing_targets': [t.model_dump() for t in request.publishing_targets],
            'auto_publish': request.auto_publish,
            'metadata': request.metadata
        }
        
        # Submit to Celery
        task = generate_and_publish.apply_async(args=[workflow_data])
        
        logger.info(f"Workflow submitted with ID: {task.id}")
        
        # Return immediate response
        return WorkflowResponse(
            workflow_id=task.id,
            status=WorkflowStatus.PENDING,
            progress_percentage=0,
            current_step="Workflow queued for execution"
        )
        
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )


@router.get(
    "/status/{workflow_id}",
    response_model=WorkflowResponse,
    summary="Get Workflow Status",
    description="Check the status of a running or completed workflow"
)
async def get_workflow_status(workflow_id: str):
    """
    Get the current status of a workflow.
    
    This allows users to poll for progress and results.
    """
    try:
        # Get task result from Celery
        task_result = AsyncResult(workflow_id, app=celery_app)
        
        # Build response based on task state
        if task_result.state == 'PENDING':
            return WorkflowResponse(
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                progress_percentage=0,
                current_step="Waiting to start"
            )
        
        elif task_result.state == 'PROGRESS':
            meta = task_result.info or {}
            return WorkflowResponse(
                workflow_id=workflow_id,
                status=WorkflowStatus.GENERATING_CONTENT,
                progress_percentage=meta.get('progress', 0),
                current_step=meta.get('step', 'Processing...')
            )
        
        elif task_result.state == 'SUCCESS':
            result = task_result.result or {}
            
            # Extract content info
            content = result.get('content', {})
            
            # Extract publishing results
            publishing_results = []
            for pr in result.get('publishing_results', []):
                publishing_results.append({
                    'platform': pr.get('platform'),
                    'success': pr.get('success', False),
                    'post_id': pr.get('post_id'),
                    'post_url': pr.get('post_url'),
                    'error_message': pr.get('error_message')
                })
            
            return WorkflowResponse(
                workflow_id=workflow_id,
                status=WorkflowStatus.PUBLISHED,
                content_generated=True,
                article_title=content.get('title'),
                word_count=content.get('word_count'),
                publishing_results=publishing_results,
                progress_percentage=100,
                current_step="Completed",
                completed_at=result.get('completed_at')
            )
        
        elif task_result.state == 'FAILURE':
            error = str(task_result.info) if task_result.info else "Unknown error"
            return WorkflowResponse(
                workflow_id=workflow_id,
                status=WorkflowStatus.FAILED,
                progress_percentage=0,
                error_message=error
            )
        
        else:
            return WorkflowResponse(
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                progress_percentage=0,
                current_step=f"State: {task_result.state}"
            )
        
    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.post(
    "/execute/bulk",
    response_model=BulkWorkflowResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute Bulk Workflows",
    description="Execute multiple workflows at once"
)
async def execute_bulk_workflows(request: BulkWorkflowRequest):
    """
    Execute multiple workflows simultaneously.
    
    This is for power users who want to generate and publish
    multiple articles at once.
    """
    try:
        logger.info(f"Executing {len(request.workflows)} workflows")
        
        workflows = []
        
        for workflow_request in request.workflows:
            workflow_data = {
                'content_params': workflow_request.content_params.model_dump(),
                'publishing_targets': [t.model_dump() for t in workflow_request.publishing_targets],
                'auto_publish': workflow_request.auto_publish,
                'metadata': workflow_request.metadata
            }
            
            # Submit to Celery
            task = generate_and_publish.apply_async(args=[workflow_data])
            
            workflows.append(WorkflowResponse(
                workflow_id=task.id,
                status=WorkflowStatus.PENDING,
                progress_percentage=0,
                current_step="Workflow queued"
            ))
        
        return BulkWorkflowResponse(
            total=len(workflows),
            in_progress=len(workflows),
            workflows=workflows
        )
        
    except Exception as e:
        logger.error(f"Failed to execute bulk workflows: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute bulk workflows: {str(e)}"
        )


@router.delete(
    "/cancel/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Workflow",
    description="Cancel a running workflow"
)
async def cancel_workflow(workflow_id: str):
    """
    Cancel a running workflow.
    
    Note: This may not stop a workflow that's already in progress,
    but it will prevent it from continuing to the next step.
    """
    try:
        celery_app.control.revoke(workflow_id, terminate=True)
        logger.info(f"Workflow {workflow_id} cancelled")
        return None
        
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}"
        )


@router.get(
    "/health",
    summary="Service Health Check",
    description="Check if the orchestrator service is healthy"
)
async def health_check():
    """
    Health check endpoint.
    """
    # Check Celery connection
    celery_ok = False
    try:
        celery_app.control.inspect().stats()
        celery_ok = True
    except Exception as e:
        logger.warning(f"Celery health check failed: {e}")
    
    return {
        "status": "healthy",
        "service": "orchestrator-api",
        "celery_connected": celery_ok,
        "endpoints": {
            "execute": "/api/v1/workflow/execute",
            "status": "/api/v1/workflow/status/{workflow_id}",
            "bulk": "/api/v1/workflow/execute/bulk",
            "cancel": "/api/v1/workflow/cancel/{workflow_id}"
        }
    }

