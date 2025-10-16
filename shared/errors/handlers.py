"""
Global Error Handlers

This module provides centralized error handling for FastAPI applications.
"""

import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from .exceptions import AutoPublisherException, to_http_exception


logger = logging.getLogger(__name__)


async def autopublisher_exception_handler(
    request: Request,
    exc: AutoPublisherException
) -> JSONResponse:
    """
    Handler for custom AutoPublisher exceptions.
    
    Args:
        request: FastAPI request
        exc: Custom exception instance
        
    Returns:
        JSON response with error details
    """
    # Log the error
    logger.error(
        f"AutoPublisher error: {exc.error_code}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    # Convert to HTTP exception
    http_exc = to_http_exception(exc)
    
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError]
) -> JSONResponse:
    """
    Handler for validation errors.
    
    Args:
        request: FastAPI request
        exc: Validation error instance
        
    Returns:
        JSON response with validation error details
    """
    errors = []
    
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.url.path}",
        extra={
            "errors": errors,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "errors": errors
            }
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler for unexpected exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception instance
        
    Returns:
        JSON response with generic error message
    """
    # Log the error with full traceback
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    # Don't expose internal error details in production
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": {}
        }
    )


def register_error_handlers(app):
    """
    Register all error handlers with FastAPI app.
    
    Usage:
        from fastapi import FastAPI
        from shared.errors.handlers import register_error_handlers
        
        app = FastAPI()
        register_error_handlers(app)
    
    Args:
        app: FastAPI application instance
    """
    # Custom exceptions
    app.add_exception_handler(AutoPublisherException, autopublisher_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(PydanticValidationError, validation_exception_handler)
    
    # Generic exceptions
    app.add_exception_handler(Exception, generic_exception_handler)

