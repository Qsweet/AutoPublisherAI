"""
Professional Logging System

Centralized logging configuration for all services.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        return json.dumps(log_data)


def setup_logging(
    service_name: str,
    log_level: str = "INFO",
    log_dir: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Setup logging configuration for a service.
    
    Args:
        service_name: Name of the service
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (None = logs to stdout only)
        json_format: Use JSON format for logs
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Choose formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '[%(request_id)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handlers (if log_dir specified)
    if log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # General log file (rotating by size)
        general_log = log_dir / f"{service_name}.log"
        file_handler = RotatingFileHandler(
            general_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error log file (rotating by time)
        error_log = log_dir / f"{service_name}_error.log"
        error_handler = TimedRotatingFileHandler(
            error_log,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


class RequestLogger:
    """
    Context manager for request logging with timing.
    """
    
    def __init__(self, logger: logging.Logger, request_id: str, endpoint: str):
        self.logger = logger
        self.request_id = request_id
        self.endpoint = endpoint
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            f"Request started: {self.endpoint}",
            extra={'request_id': self.request_id}
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds() * 1000
        
        if exc_type is None:
            self.logger.info(
                f"Request completed: {self.endpoint}",
                extra={
                    'request_id': self.request_id,
                    'duration': duration
                }
            )
        else:
            self.logger.error(
                f"Request failed: {self.endpoint} - {exc_val}",
                extra={
                    'request_id': self.request_id,
                    'duration': duration
                },
                exc_info=True
            )
        
        return False  # Don't suppress exceptions


# Default logger factory
def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name."""
    return logging.getLogger(name)

