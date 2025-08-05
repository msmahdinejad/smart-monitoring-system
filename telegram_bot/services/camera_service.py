#!/usr/bin/env python3
"""
Camera Service for Telegram Bot
Handles camera operations and video recording
"""

import os
import time  # Add this import
import logging
from typing import Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class CameraService:
    """Handle camera operations for Telegram bot"""
    
    def __init__(self, main_app_instance):
        """Initialize camera service with main app reference"""
        self.main_app = main_app_instance
        
        # Import configurations
        try:
            from config import ESP32_CAM_CONFIG, STORAGE_CONFIG
            self.esp32_config = ESP32_CAM_CONFIG
            self.storage_config = STORAGE_CONFIG
        except ImportError:
            logger.error("Failed to import camera configurations")
            raise
    
    def capture_image(self) -> Optional[bytes]:
        """Capture image from ESP32-CAM with thread safety"""
        try:
            with self.main_app.api_lock:
                image_data = self.main_app.camera.capture_image()
            
            if image_data:
                logger.info("Image captured successfully")
                return image_data
            else:
                logger.error("Failed to capture image - no data returned")
                return None
                
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    def test_camera_connection(self) -> bool:
        """Test camera connection status"""
        try:
            with self.main_app.api_lock:
                status = self.main_app.camera.test_connection()
            
            logger.info(f"Camera connection test: {'OK' if status else 'FAILED'}")
            return status
            
        except Exception as e:
            logger.error(f"Error testing camera connection: {e}")
            return False
    
    def save_temp_image(self, image_data: bytes, prefix: str = "telegram_capture") -> Optional[str]:
        """Save image data to temporary file and return path"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_image_path = f"{self.storage_config['images_directory']}/{prefix}_{timestamp}.jpg"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
            
            with open(temp_image_path, 'wb') as f:
                f.write(image_data)
            
            logger.info(f"Temporary image saved: {temp_image_path}")
            return temp_image_path
            
        except Exception as e:
            logger.error(f"Error saving temporary image: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
            return False
    
    def get_camera_info(self) -> dict:
        """Get camera information and status"""
        try:
            connection_status = self.test_camera_connection()
            
            return {
                'ip_address': self.esp32_config['ip_address'],
                'timeout': self.esp32_config['timeout'],
                'retry_count': self.esp32_config['retry_count'],
                'status': 'Online' if connection_status else 'Offline',
                'status_emoji': '🟢' if connection_status else '🔴'
            }
        except Exception as e:
            logger.error(f"Error getting camera info: {e}")
            return {
                'ip_address': 'Unknown',
                'timeout': 0,
                'retry_count': 0,
                'status': 'Error',
                'status_emoji': '❌'
            }

class VideoService:
    """Handle video recording operations for Telegram bot with new API"""
    
    def __init__(self, main_app_instance):
        """Initialize video service with main app reference"""
        self.main_app = main_app_instance
        
        # Import configurations
        try:
            from config import STORAGE_CONFIG
            self.storage_config = STORAGE_CONFIG
        except ImportError:
            logger.error("Failed to import storage configurations")
            raise
    
    def test_video_recording(self, duration: int = 10) -> Optional[str]:
        """Test video recording functionality with new API"""
        try:
            test_session_id = "telegram_test_" + datetime.now().strftime('%H%M%S')
            logger.info(f"Starting Video Only test for session: {test_session_id}")
            
            # Use the main app's video recorder
            video_recorder = self.main_app.video_recorder
            
            # Start recording
            success = video_recorder.start_recording(duration, test_session_id)
            if not success:
                logger.error("Failed to start video recording")
                return None
            
            # Wait for recording to complete
            max_wait = duration + 5  # Extra 5 seconds for processing
            wait_time = 0
            check_interval = 0.5
            
            while video_recorder.is_recording and wait_time < max_wait:
                time.sleep(check_interval)
                wait_time += check_interval
            
            # Wait a bit more for video processing
            time.sleep(2)
            
            # Get the video path
            video_path = getattr(video_recorder, 'last_video_path', None)
            
            if video_path and os.path.exists(video_path):
                logger.info(f"Video test successful: {video_path}")
                return video_path
            else:
                logger.error("Video test failed - no video file created")
                return None
                
        except Exception as e:
            logger.error(f"Error in video test: {e}")
            return None
    
    def get_video_status(self) -> dict:
        """Get video recording status"""
        try:
            video_recorder = self.main_app.video_recorder
            is_recording = getattr(video_recorder, 'is_recording', False)
            
            return {
                'is_recording': is_recording,
                'status': 'Recording' if is_recording else 'Standby',
                'status_emoji': '🎥' if is_recording else '⏸️',
                'videos_directory': f"{self.storage_config['images_directory']}/videos"
            }
        except Exception as e:
            logger.error(f"Error getting video status: {e}")
            return {
                'is_recording': False,
                'status': 'Unknown',
                'status_emoji': '❓',
                'videos_directory': 'Unknown'
            }