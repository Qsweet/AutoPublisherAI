"""
Celery Task Monitoring Utilities

Provides monitoring and tracking for Celery tasks.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from celery import Celery
from celery.result import AsyncResult
import redis


class CeleryMonitor:
    """
    Monitor Celery tasks and workers.
    """
    
    def __init__(self, celery_app: Celery, redis_url: str):
        """
        Initialize Celery monitor.
        
        Args:
            celery_app: Celery application instance
            redis_url: Redis connection URL
        """
        self.app = celery_app
        self.redis_client = redis.from_url(redis_url)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a specific task.
        
        Args:
            task_id: Task ID
        
        Returns:
            Dictionary with task status information
        """
        result = AsyncResult(task_id, app=self.app)
        
        return {
            'task_id': task_id,
            'state': result.state,
            'ready': result.ready(),
            'successful': result.successful() if result.ready() else None,
            'failed': result.failed() if result.ready() else None,
            'result': result.result if result.ready() else None,
            'traceback': result.traceback if result.failed() else None,
            'info': result.info,
        }
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active tasks.
        
        Returns:
            List of active tasks with their information
        """
        inspect = self.app.control.inspect()
        active = inspect.active()
        
        if not active:
            return []
        
        tasks = []
        for worker, task_list in active.items():
            for task in task_list:
                tasks.append({
                    'worker': worker,
                    'task_id': task.get('id'),
                    'name': task.get('name'),
                    'args': task.get('args'),
                    'kwargs': task.get('kwargs'),
                    'time_start': task.get('time_start'),
                })
        
        return tasks
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Get list of scheduled (queued) tasks.
        
        Returns:
            List of scheduled tasks
        """
        inspect = self.app.control.inspect()
        scheduled = inspect.scheduled()
        
        if not scheduled:
            return []
        
        tasks = []
        for worker, task_list in scheduled.items():
            for task in task_list:
                tasks.append({
                    'worker': worker,
                    'task_id': task.get('request', {}).get('id'),
                    'name': task.get('request', {}).get('name'),
                    'eta': task.get('eta'),
                })
        
        return tasks
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """
        Get statistics about Celery workers.
        
        Returns:
            Dictionary with worker statistics
        """
        inspect = self.app.control.inspect()
        
        stats = inspect.stats()
        active = inspect.active()
        registered = inspect.registered()
        
        if not stats:
            return {'workers': 0, 'details': []}
        
        workers = []
        for worker_name, worker_stats in stats.items():
            workers.append({
                'name': worker_name,
                'active_tasks': len(active.get(worker_name, [])) if active else 0,
                'registered_tasks': len(registered.get(worker_name, [])) if registered else 0,
                'pool': worker_stats.get('pool', {}),
                'total_tasks': worker_stats.get('total', {}),
            })
        
        return {
            'workers': len(workers),
            'details': workers
        }
    
    def get_queue_length(self, queue_name: str = 'celery') -> int:
        """
        Get number of tasks in a specific queue.
        
        Args:
            queue_name: Name of the queue
        
        Returns:
            Number of tasks in queue
        """
        try:
            return self.redis_client.llen(queue_name)
        except Exception:
            return 0
    
    def get_failed_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of recently failed tasks.
        
        Note: This requires task results to be stored in backend.
        
        Args:
            limit: Maximum number of failed tasks to return
        
        Returns:
            List of failed tasks
        """
        # This is a simplified version
        # In production, you'd query the result backend
        failed_tasks = []
        
        # Get task IDs from Redis (if stored)
        task_keys = self.redis_client.keys('celery-task-meta-*')
        
        for key in task_keys[:limit]:
            task_id = key.decode('utf-8').replace('celery-task-meta-', '')
            status = self.get_task_status(task_id)
            
            if status['failed']:
                failed_tasks.append(status)
        
        return failed_tasks
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """
        Revoke (cancel) a task.
        
        Args:
            task_id: Task ID to revoke
            terminate: Whether to terminate if task is running
        
        Returns:
            True if revoked successfully
        """
        try:
            self.app.control.revoke(task_id, terminate=terminate)
            return True
        except Exception:
            return False
    
    def purge_queue(self, queue_name: str = 'celery') -> int:
        """
        Purge all tasks from a queue.
        
        Args:
            queue_name: Name of the queue to purge
        
        Returns:
            Number of tasks purged
        """
        try:
            return self.app.control.purge()
        except Exception:
            return 0
    
    def get_task_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get task execution metrics for the last N hours.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Dictionary with metrics
        """
        # This is a simplified version
        # In production, you'd track this in a time-series database
        
        active_tasks = self.get_active_tasks()
        scheduled_tasks = self.get_scheduled_tasks()
        worker_stats = self.get_worker_stats()
        
        return {
            'period_hours': hours,
            'active_tasks': len(active_tasks),
            'scheduled_tasks': len(scheduled_tasks),
            'workers': worker_stats['workers'],
            'queue_length': self.get_queue_length(),
        }


def create_task_wrapper(monitor: CeleryMonitor):
    """
    Create a decorator to wrap Celery tasks with monitoring.
    
    Args:
        monitor: CeleryMonitor instance
    
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            task_id = func.request.id
            
            # Log task start
            monitor.redis_client.hset(
                f'task:{task_id}',
                mapping={
                    'name': func.name,
                    'start_time': datetime.utcnow().isoformat(),
                    'status': 'running',
                }
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log task success
                monitor.redis_client.hset(
                    f'task:{task_id}',
                    mapping={
                        'end_time': datetime.utcnow().isoformat(),
                        'status': 'success',
                    }
                )
                
                return result
            
            except Exception as e:
                # Log task failure
                monitor.redis_client.hset(
                    f'task:{task_id}',
                    mapping={
                        'end_time': datetime.utcnow().isoformat(),
                        'status': 'failed',
                        'error': str(e),
                    }
                )
                raise
        
        return wrapper
    return decorator

