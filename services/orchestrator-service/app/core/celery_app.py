"""
Celery Application Configuration

This sets up Celery for background task processing.
Celery is THE industry standard for distributed task queues.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "autopublisher",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
    include=['app.tasks.workflow']
)

# Configure Celery
celery_app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=settings.TASK_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.TASK_TIMEOUT_SECONDS - 60,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Beat schedule (for periodic tasks)
    beat_schedule={
        # Example: Clean up old tasks every day at 3 AM
        'cleanup-old-tasks': {
            'task': 'app.tasks.workflow.cleanup_old_tasks',
            'schedule': crontab(hour=3, minute=0),
        },
    },
)

# Task routes (optional: route specific tasks to specific queues)
celery_app.conf.task_routes = {
    'app.tasks.workflow.generate_and_publish': {'queue': 'default'},
    'app.tasks.workflow.generate_content_task': {'queue': 'content'},
    'app.tasks.workflow.publish_content_task': {'queue': 'publishing'},
}


if __name__ == '__main__':
    celery_app.start()

