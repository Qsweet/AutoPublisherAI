"""
Workflow Data Models

Models for orchestrating the complete content generation and publishing workflow.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    GENERATING_CONTENT = "generating_content"
    CONTENT_GENERATED = "content_generated"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ContentGenerationParams(BaseModel):
    """Parameters for content generation."""
    topic: str = Field(..., description="Main topic for the article")
    language: str = Field(default="ar", description="Content language")
    target_length: int = Field(default=1500, description="Target word count")
    seo_level: str = Field(default="high", description="SEO optimization level")
    tone: str = Field(default="professional", description="Content tone")
    target_keywords: Optional[List[str]] = Field(None, description="Target keywords")
    include_image: bool = Field(default=True, description="Generate featured image")
    include_faq: bool = Field(default=True, description="Include FAQ section")
    target_audience: Optional[str] = Field(None, description="Target audience")


class PublishingTarget(BaseModel):
    """A single publishing target (platform + config)."""
    platform: str = Field(..., description="Platform name (wordpress, instagram, etc.)")
    
    # WordPress-specific
    post_status: Optional[str] = Field(None, description="WordPress post status")
    categories: Optional[List[str]] = Field(None, description="WordPress categories")
    tags: Optional[List[str]] = Field(None, description="WordPress tags")
    
    # Instagram-specific
    hashtags: Optional[List[str]] = Field(None, description="Instagram hashtags")
    location_id: Optional[str] = Field(None, description="Instagram location ID")
    
    # Scheduling
    schedule_time: Optional[datetime] = Field(None, description="When to publish")


class WorkflowRequest(BaseModel):
    """
    Request to execute a complete workflow.
    
    This represents the user's request: "Generate content and publish it".
    """
    # Content generation
    content_params: ContentGenerationParams = Field(..., description="Content generation parameters")
    
    # Publishing targets
    publishing_targets: List[PublishingTarget] = Field(
        ...,
        min_length=1,
        description="Where to publish the content"
    )
    
    # Workflow options
    auto_publish: bool = Field(
        default=True,
        description="Automatically publish after generation"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_params": {
                    "topic": "فوائد العمل عن بعد للشركات الناشئة",
                    "language": "ar",
                    "target_length": 1500,
                    "seo_level": "high",
                    "include_image": True,
                    "include_faq": True
                },
                "publishing_targets": [
                    {
                        "platform": "wordpress",
                        "post_status": "publish",
                        "categories": ["تقنية", "عمل"],
                        "tags": ["عمل عن بعد", "شركات ناشئة"]
                    },
                    {
                        "platform": "instagram",
                        "hashtags": ["عمل_عن_بعد", "تقنية", "شركات_ناشئة"]
                    }
                ],
                "auto_publish": True
            }
        }


class WorkflowResult(BaseModel):
    """Result of a single publishing action."""
    platform: str = Field(..., description="Platform name")
    success: bool = Field(..., description="Whether publishing succeeded")
    post_id: Optional[str] = Field(None, description="Platform post ID")
    post_url: Optional[str] = Field(None, description="URL of published content")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class WorkflowResponse(BaseModel):
    """
    Response for a workflow execution.
    
    This tracks the entire workflow from start to finish.
    """
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: WorkflowStatus = Field(..., description="Current workflow status")
    
    # Content generation
    content_generated: bool = Field(default=False, description="Whether content was generated")
    article_title: Optional[str] = Field(None, description="Generated article title")
    word_count: Optional[int] = Field(None, description="Article word count")
    
    # Publishing results
    publishing_results: List[WorkflowResult] = Field(
        default_factory=list,
        description="Results for each publishing target"
    )
    
    # Progress tracking
    progress_percentage: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current step description")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if workflow failed")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="When workflow completed")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BulkWorkflowRequest(BaseModel):
    """
    Request to execute multiple workflows.
    
    This is for power users who want to generate and publish
    multiple articles at once.
    """
    workflows: List[WorkflowRequest] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of workflow requests"
    )
    
    parallel_execution: bool = Field(
        default=True,
        description="Execute workflows in parallel"
    )
    
    stop_on_first_error: bool = Field(
        default=False,
        description="Stop if one workflow fails"
    )


class BulkWorkflowResponse(BaseModel):
    """Response for bulk workflow execution."""
    total: int = Field(..., description="Total workflows requested")
    successful: int = Field(default=0, description="Number of successful workflows")
    failed: int = Field(default=0, description="Number of failed workflows")
    in_progress: int = Field(default=0, description="Number of workflows still in progress")
    workflows: List[WorkflowResponse] = Field(..., description="Individual workflow responses")


class ScheduledWorkflow(BaseModel):
    """A workflow scheduled for future execution."""
    schedule_id: str = Field(..., description="Unique schedule ID")
    workflow_request: WorkflowRequest = Field(..., description="The workflow to execute")
    schedule_time: datetime = Field(..., description="When to execute")
    recurring: bool = Field(default=False, description="Whether this is a recurring schedule")
    cron_expression: Optional[str] = Field(None, description="Cron expression for recurring schedules")
    enabled: bool = Field(default=True, description="Whether schedule is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)

