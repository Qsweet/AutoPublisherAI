"""Logging setup for content-service."""
import sys
from pathlib import Path

# Add shared directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / 'shared'))

try:
    from logging.logger import setup_logging
    logger = setup_logging(
        service_name="content-service",
        log_level="INFO",
        json_format=False
    )
except ImportError:
    import logging
    logger = logging.getLogger("content-service")
    logging.basicConfig(level=logging.INFO)

__all__ = ['logger']
