"""
Logging Configuration
"""
import logging
import sys
from app.core.config import settings


def setup_logging():
    """Configure application logging"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
