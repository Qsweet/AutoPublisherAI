"""
Retry Logic Utilities

This module provides retry mechanisms for handling transient failures.
Uses exponential backoff with jitter for optimal retry behavior.
"""

import asyncio
import logging
from typing import Callable, TypeVar, Optional, Type, Tuple
from functools import wraps
import random


logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
            exceptions: Tuple of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.exceptions = exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Args:
            attempt: Current attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        # Calculate exponential backoff
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        # Add jitter if enabled
        if self.jitter:
            delay = delay * (0.5 + random.random())
        
        return delay


def retry_async(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying async functions with exponential backoff.
    
    Usage:
        @retry_async(max_attempts=3, initial_delay=1.0)
        async def call_external_api():
            # API call that might fail
            pass
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function with retry logic
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        exceptions=exceptions
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                    
                except config.exceptions as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt == config.max_attempts - 1:
                        break
                    
                    # Calculate delay
                    delay = config.calculate_delay(attempt)
                    
                    # Log retry
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_attempts": config.max_attempts,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
            
            # All retries failed
            logger.error(
                f"All {config.max_attempts} retry attempts failed for {func.__name__}",
                extra={
                    "function": func.__name__,
                    "max_attempts": config.max_attempts,
                    "final_error": str(last_exception)
                }
            )
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying synchronous functions with exponential backoff.
    
    Usage:
        @retry_sync(max_attempts=3, initial_delay=1.0)
        def call_external_api():
            # API call that might fail
            pass
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        exceptions: Tuple of exceptions to retry on
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function with retry logic
    """
    import time
    
    config = RetryConfig(
        max_attempts=max_attempts,
        initial_delay=initial_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        exceptions=exceptions
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                    
                except config.exceptions as e:
                    last_exception = e
                    
                    # Don't retry on last attempt
                    if attempt == config.max_attempts - 1:
                        break
                    
                    # Calculate delay
                    delay = config.calculate_delay(attempt)
                    
                    # Log retry
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{config.max_attempts} for {func.__name__}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_attempts": config.max_attempts,
                            "delay": delay,
                            "error": str(e)
                        }
                    )
                    
                    # Call on_retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retry
                    time.sleep(delay)
            
            # All retries failed
            logger.error(
                f"All {config.max_attempts} retry attempts failed for {func.__name__}",
                extra={
                    "function": func.__name__,
                    "max_attempts": config.max_attempts,
                    "final_error": str(last_exception)
                }
            )
            
            raise last_exception
        
        return wrapper
    return decorator


# Predefined retry configurations for common scenarios

# For external API calls (OpenAI, etc.)
retry_external_api = lambda func: retry_async(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)(func)

# For database operations
retry_database = lambda func: retry_async(
    max_attempts=5,
    initial_delay=0.5,
    max_delay=10.0,
    exponential_base=2.0,
    jitter=True
)(func)

# For network requests
retry_network = lambda func: retry_async(
    max_attempts=3,
    initial_delay=1.0,
    max_delay=20.0,
    exponential_base=2.0,
    jitter=True
)(func)

