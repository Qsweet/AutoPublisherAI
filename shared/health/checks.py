"""
Health Check System

This module provides health check endpoints for monitoring service status.
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import logging


logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """
    Health check result.
    """
    
    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[float] = None
    ):
        self.name = name
        self.status = status
        self.message = message or status.value
        self.details = details or {}
        self.response_time_ms = response_time_ms
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp
        }


class HealthChecker:
    """
    Health check manager.
    
    Manages multiple health checks and provides aggregated status.
    """
    
    def __init__(self, service_name: str):
        """
        Initialize health checker.
        
        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.checks: Dict[str, Callable] = {}
    
    def register_check(self, name: str, check_func: Callable):
        """
        Register a health check function.
        
        Args:
            name: Name of the check
            check_func: Async function that returns HealthCheck
        """
        self.checks[name] = check_func
    
    async def run_check(self, name: str) -> HealthCheck:
        """
        Run a single health check.
        
        Args:
            name: Name of the check to run
            
        Returns:
            HealthCheck result
        """
        check_func = self.checks.get(name)
        if not check_func:
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check '{name}' not found"
            )
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await check_func()
            end_time = asyncio.get_event_loop().time()
            
            response_time_ms = (end_time - start_time) * 1000
            result.response_time_ms = response_time_ms
            
            return result
            
        except Exception as e:
            logger.error(f"Health check '{name}' failed: {e}", exc_info=True)
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {str(e)}"
            )
    
    async def run_all_checks(self) -> List[HealthCheck]:
        """
        Run all registered health checks.
        
        Returns:
            List of HealthCheck results
        """
        tasks = [self.run_check(name) for name in self.checks.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to unhealthy checks
        health_checks = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                name = list(self.checks.keys())[i]
                health_checks.append(HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {str(result)}"
                ))
            else:
                health_checks.append(result)
        
        return health_checks
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get aggregated health status.
        
        Returns:
            Dictionary with overall status and individual check results
        """
        checks = await self.run_all_checks()
        
        # Determine overall status
        statuses = [check.status for check in checks]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            overall_status = HealthStatus.UNHEALTHY
        else:
            overall_status = HealthStatus.DEGRADED
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [check.to_dict() for check in checks]
        }


# Common health check functions

async def check_database(db_connection) -> HealthCheck:
    """
    Check database connectivity.
    
    Args:
        db_connection: Database connection object
        
    Returns:
        HealthCheck result
    """
    try:
        # Try a simple query
        await db_connection.execute("SELECT 1")
        
        return HealthCheck(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database connection is healthy"
        )
        
    except Exception as e:
        return HealthCheck(
            name="database",
            status=HealthStatus.UNHEALTHY,
            message=f"Database connection failed: {str(e)}"
        )


async def check_redis(redis_client) -> HealthCheck:
    """
    Check Redis connectivity.
    
    Args:
        redis_client: Redis client object
        
    Returns:
        HealthCheck result
    """
    try:
        # Try a ping
        await redis_client.ping()
        
        return HealthCheck(
            name="redis",
            status=HealthStatus.HEALTHY,
            message="Redis connection is healthy"
        )
        
    except Exception as e:
        return HealthCheck(
            name="redis",
            status=HealthStatus.UNHEALTHY,
            message=f"Redis connection failed: {str(e)}"
        )


async def check_external_service(
    service_name: str,
    url: str,
    timeout: float = 5.0
) -> HealthCheck:
    """
    Check external service availability.
    
    Args:
        service_name: Name of the service
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        HealthCheck result
    """
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return HealthCheck(
                        name=service_name,
                        status=HealthStatus.HEALTHY,
                        message=f"{service_name} is available"
                    )
                else:
                    return HealthCheck(
                        name=service_name,
                        status=HealthStatus.DEGRADED,
                        message=f"{service_name} returned status {response.status}"
                    )
                    
    except Exception as e:
        return HealthCheck(
            name=service_name,
            status=HealthStatus.UNHEALTHY,
            message=f"{service_name} is unavailable: {str(e)}"
        )


def create_health_router(health_checker: HealthChecker):
    """
    Create FastAPI router with health check endpoints.
    
    Usage:
        from fastapi import FastAPI
        from shared.health.checks import HealthChecker, create_health_router
        
        app = FastAPI()
        health_checker = HealthChecker("my-service")
        health_router = create_health_router(health_checker)
        app.include_router(health_router)
    
    Args:
        health_checker: HealthChecker instance
        
    Returns:
        FastAPI APIRouter with health endpoints
    """
    from fastapi import APIRouter, Response, status
    
    router = APIRouter(tags=["Health"])
    
    @router.get("/health")
    async def health_check():
        """
        Basic health check endpoint.
        
        Returns 200 if service is healthy.
        """
        health_status = await health_checker.get_health_status()
        
        # Return appropriate status code
        if health_status["status"] == HealthStatus.HEALTHY.value:
            return health_status
        elif health_status["status"] == HealthStatus.DEGRADED.value:
            return Response(
                content=str(health_status),
                status_code=status.HTTP_200_OK,
                media_type="application/json"
            )
        else:
            return Response(
                content=str(health_status),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json"
            )
    
    @router.get("/health/live")
    async def liveness_check():
        """
        Kubernetes liveness probe endpoint.
        
        Returns 200 if service is running.
        """
        return {
            "service": health_checker.service_name,
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @router.get("/health/ready")
    async def readiness_check():
        """
        Kubernetes readiness probe endpoint.
        
        Returns 200 if service is ready to accept traffic.
        """
        health_status = await health_checker.get_health_status()
        
        if health_status["status"] in [HealthStatus.HEALTHY.value, HealthStatus.DEGRADED.value]:
            return health_status
        else:
            return Response(
                content=str(health_status),
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/json"
            )
    
    return router

