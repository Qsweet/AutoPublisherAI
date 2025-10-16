"""
Rate Limiting Middleware

This module implements rate limiting to prevent API abuse and DDoS attacks.
Uses Redis for distributed rate limiting across multiple instances.
"""

from typing import Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import hashlib
from redis import Redis
from functools import wraps
import asyncio


class RateLimiter:
    """
    Redis-based rate limiter for API endpoints.
    
    Implements the Token Bucket algorithm for smooth rate limiting.
    """
    
    def __init__(
        self,
        redis_client: Redis,
        default_rate: int = 60,
        default_period: int = 60
    ):
        """
        Initialize rate limiter.
        
        Args:
            redis_client: Redis client instance
            default_rate: Default number of requests allowed
            default_period: Time period in seconds
        """
        self.redis = redis_client
        self.default_rate = default_rate
        self.default_period = default_period
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client.
        
        Uses IP address and optional API key for identification.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Unique client identifier
        """
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get API key if present
        api_key = request.headers.get("X-API-Key", "")
        
        # Create unique identifier
        identifier = f"{client_ip}:{api_key}"
        
        # Hash for privacy
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """
        Generate Redis key for rate limiting.
        
        Args:
            identifier: Client identifier
            endpoint: API endpoint path
            
        Returns:
            Redis key string
        """
        return f"rate_limit:{identifier}:{endpoint}"
    
    async def check_rate_limit(
        self,
        request: Request,
        rate: Optional[int] = None,
        period: Optional[int] = None
    ) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            request: FastAPI request object
            rate: Number of requests allowed (overrides default)
            period: Time period in seconds (overrides default)
            
        Returns:
            True if within limit, raises HTTPException if exceeded
        """
        rate = rate or self.default_rate
        period = period or self.default_period
        
        # Get client identifier
        identifier = self._get_client_identifier(request)
        
        # Get endpoint path
        endpoint = request.url.path
        
        # Generate Redis key
        key = self._get_rate_limit_key(identifier, endpoint)
        
        try:
            # Get current count
            current = self.redis.get(key)
            
            if current is None:
                # First request, set counter
                self.redis.setex(key, period, 1)
                return True
            
            current_count = int(current)
            
            if current_count >= rate:
                # Rate limit exceeded
                ttl = self.redis.ttl(key)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Please try again in {ttl} seconds.",
                        "retry_after": ttl,
                        "limit": rate,
                        "period": period
                    }
                )
            
            # Increment counter
            self.redis.incr(key)
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            # If Redis fails, allow the request (fail open)
            # Log the error in production
            print(f"Rate limiter error: {e}")
            return True
    
    def limit(
        self,
        rate: Optional[int] = None,
        period: Optional[int] = None
    ):
        """
        Decorator for rate limiting endpoints.
        
        Usage:
            @app.get("/api/endpoint")
            @rate_limiter.limit(rate=10, period=60)
            async def endpoint():
                ...
        
        Args:
            rate: Number of requests allowed
            period: Time period in seconds
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get request from kwargs
                request = kwargs.get("request")
                if not request:
                    # Try to find request in args
                    for arg in args:
                        if isinstance(arg, Request):
                            request = arg
                            break
                
                if request:
                    await self.check_rate_limit(request, rate, period)
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator


class RateLimitMiddleware:
    """
    FastAPI middleware for global rate limiting.
    
    Applies rate limiting to all requests automatically.
    """
    
    def __init__(
        self,
        app,
        redis_client: Redis,
        rate: int = 60,
        period: int = 60,
        exclude_paths: Optional[list] = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            redis_client: Redis client instance
            rate: Number of requests allowed
            period: Time period in seconds
            exclude_paths: List of paths to exclude from rate limiting
        """
        self.app = app
        self.rate_limiter = RateLimiter(redis_client, rate, period)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
    
    async def __call__(self, request: Request, call_next):
        """
        Process request through rate limiter.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        try:
            # Check rate limit
            await self.rate_limiter.check_rate_limit(request)
            
            # Process request
            response = await call_next(request)
            
            return response
            
        except HTTPException as e:
            # Return rate limit error
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail
            )


# Helper function to create rate limiter from Redis URL
def create_rate_limiter(redis_url: str, rate: int = 60, period: int = 60) -> RateLimiter:
    """
    Create rate limiter instance from Redis URL.
    
    Args:
        redis_url: Redis connection URL
        rate: Number of requests allowed
        period: Time period in seconds
        
    Returns:
        RateLimiter instance
    """
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    return RateLimiter(redis_client, rate, period)

