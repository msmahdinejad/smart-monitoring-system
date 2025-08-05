"""
Directory Setup Utilities
Creates all required directories for the application
"""

import os
import logging

try:
    from config import STORAGE_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)


def create_directories():
    """Create all required directories"""
    directories = [
        STORAGE_CONFIG['images_directory'],
        STORAGE_CONFIG['logs_directory'],
        STORAGE_CONFIG['backups_directory'],
        os.path.join(STORAGE_CONFIG['images_directory'], 'videos')
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")