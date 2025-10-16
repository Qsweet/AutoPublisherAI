"""
Custom Exception Classes

This module defines custom exceptions for better error handling across services.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class AutoPublisherException(Exception):
    """Base exception for all AutoPublisher errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ServiceUnavailableError(AutoPublisherException):
    """Raised when an external service is unavailable."""
    
    def __init__(
        self,
        service_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"{service_name} service is temporarily unavailable"
        super().__init__(message, "SERVICE_UNAVAILABLE", details)
        self.service_name = service_name


class OpenAIError(ServiceUnavailableError):
    """Raised when OpenAI API fails."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__("OpenAI", message, details)


class DatabaseError(AutoPublisherException):
    """Raised when database operations fail."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or "Database operation failed"
        super().__init__(message, "DATABASE_ERROR", details)


class ValidationError(AutoPublisherException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)


class AuthenticationError(AutoPublisherException):
    """Raised when authentication fails."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or "Authentication failed"
        super().__init__(message, "AUTHENTICATION_ERROR", details)


class AuthorizationError(AutoPublisherException):
    """Raised when user doesn't have permission."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or "Insufficient permissions"
        super().__init__(message, "AUTHORIZATION_ERROR", details)


class ResourceNotFoundError(AutoPublisherException):
    """Raised when a requested resource is not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, "RESOURCE_NOT_FOUND", details)


class RateLimitError(AutoPublisherException):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        retry_after: int,
        limit: int,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Rate limit exceeded. Try again in {retry_after} seconds."
        details = details or {}
        details.update({"retry_after": retry_after, "limit": limit})
        super().__init__(message, "RATE_LIMIT_EXCEEDED", details)


class ContentGenerationError(AutoPublisherException):
    """Raised when content generation fails."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or "Content generation failed"
        super().__init__(message, "CONTENT_GENERATION_ERROR", details)


class PublishingError(AutoPublisherException):
    """Raised when publishing to a platform fails."""
    
    def __init__(
        self,
        platform: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"Failed to publish to {platform}"
        details = details or {}
        details["platform"] = platform
        super().__init__(message, "PUBLISHING_ERROR", details)


class WorkflowError(AutoPublisherException):
    """Raised when workflow execution fails."""
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = message or "Workflow execution failed"
        super().__init__(message, "WORKFLOW_ERROR", details)


class ConfigurationError(AutoPublisherException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, "CONFIGURATION_ERROR", details)


# Mapping of custom exceptions to HTTP status codes
EXCEPTION_STATUS_MAP = {
    ServiceUnavailableError: status.HTTP_503_SERVICE_UNAVAILABLE,
    OpenAIError: status.HTTP_503_SERVICE_UNAVAILABLE,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    ResourceNotFoundError: status.HTTP_404_NOT_FOUND,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    ContentGenerationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    PublishingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    WorkflowError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ConfigurationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
}


def to_http_exception(exc: AutoPublisherException) -> HTTPException:
    """
    Convert custom exception to FastAPI HTTPException.
    
    Args:
        exc: Custom exception instance
        
    Returns:
        HTTPException with appropriate status code and details
    """
    status_code = EXCEPTION_STATUS_MAP.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    detail = {
        "error": exc.error_code,
        "message": exc.message,
        "details": exc.details
    }
    
    return HTTPException(status_code=status_code, detail=detail)

