"""
Camera Service
Handles ESP32-CAM communication and image capture
"""

import time
import logging
import requests

try:
    from config import ESP32_CAM_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)


class CameraService:
    """ESP32-CAM controller with configurable retry logic"""
    
    def __init__(self):
        self.ip = ESP32_CAM_CONFIG['ip_address']
        self.timeout = ESP32_CAM_CONFIG['timeout']
        self.retry_count = ESP32_CAM_CONFIG['retry_count']
        self.retry_delay = ESP32_CAM_CONFIG['retry_delay']
        self.session = requests.Session()
        self.session.timeout = self.timeout
        
    def capture_image(self):
        """Capture image with configurable retry logic"""
        for attempt in range(self.retry_count):
            try:
                response = self.session.get(f"http://{self.ip}/capture", timeout=self.timeout)
                if response.status_code == 200 and len(response.content) > 1000:
                    return response.content
            except Exception as e:
                logger.warning(f"Capture attempt {attempt + 1}/{self.retry_count} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
        return None
    
    def test_connection(self):
        """Test camera connectivity"""
        try:
            response = self.session.get(f"http://{self.ip}/status", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_stream_url(self):
        """Get camera stream URL"""
        return f"http://{self.ip}/stream"