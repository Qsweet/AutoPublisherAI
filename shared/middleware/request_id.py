"""
Request ID Middleware

Adds unique request ID to each request for tracing across microservices.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.
    
    The request ID can be:
    1. Provided by client in X-Request-ID header
    2. Auto-generated if not provided
    
    The request ID is:
    - Stored in request.state.request_id
    - Added to response headers as X-Request-ID
    - Available for logging and tracing
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and add request ID.
        
        Args:
            request: Incoming request
            call_next: Next middleware/endpoint
        
        Returns:
            Response with X-Request-ID header
        """
        # Get request ID from header or generate new one
        request_id = request.headers.get('X-Request-ID')
        
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store in request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response


def get_request_id(request: Request) -> str:
    """
    Get request ID from request state.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Request ID string
    """
    return getattr(request.state, 'request_id', 'unknown')

