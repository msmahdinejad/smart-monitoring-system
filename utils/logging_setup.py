"""
Logging Setup Utilities
Configures enhanced logging with file rotation
"""

import os
import logging
from logging.handlers import RotatingFileHandler

try:
    from config import LOGGING_CONFIG, STORAGE_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)


def setup_logging():
    """Setup enhanced logging with file rotation"""
    log_formatter = logging.Formatter(LOGGING_CONFIG['format'])
    
    # Create logs directory
    os.makedirs(STORAGE_CONFIG['logs_directory'], exist_ok=True)
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
    
    # Console handler
    if LOGGING_CONFIG['console_enabled']:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if LOGGING_CONFIG['file_enabled']:
        log_file = os.path.join(STORAGE_CONFIG['logs_directory'], LOGGING_CONFIG['file_name'])
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count']
        )
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)