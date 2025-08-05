"""
Monitoring Service
Main monitoring logic with thread-safe state management and immediate stop capability
"""

import os
import base64
import time
import hashlib
import threading
import logging
from datetime import datetime

from services.camera_service import CameraService
from services.video_service import VideoRecordingService
from services.ai_service import AIAnalysisService
from services.telegram_service import TelegramService
from models.database import DatabaseManager
from utils.prompt_engine import PromptEngine

try:
    from config import MONITORING_CONFIG, AI_CONFIG, IMAGES_DIR, is_ai_enabled
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)

class MonitoringService:
    """Thread-safe monitoring service with video recording support and immediate stop"""
    
    def __init__(self):
        self.camera_service = CameraService()
        self.video_service = VideoRecordingService()
        self.ai_service = AIAnalysisService()
        self.telegram_service = TelegramService()
        self.db_manager = DatabaseManager()
        
        # Thread-safe state management
        self._lock = threading.RLock()
        self._api_lock = threading.Lock()
        self._monitoring_active = False
        self._monitoring_thread = None
        self._current_session_id = None
        self._baseline_image_path = None
    
    @property
    def is_active(self):
        """Check if monitoring is currently active"""
        with self._lock:
            return self._monitoring_active
    
    @property
    def current_session_id(self):
        """Get current session ID"""
        with self._lock:
            return self._current_session_id
    
    @property
    def baseline_image_path(self):
        """Get baseline image path"""
        with self._lock:
            return self._baseline_image_path
    
    def get_monitoring_state(self):
        """Thread-safe getter for monitoring state"""
        with self._lock:
            return {
                'active': self._monitoring_active,
                'session_id': self._current_session_id,
                'baseline_path': self._baseline_image_path
            }
    
    def start_monitoring(self, interval, monitoring_type, prompt_style, custom_context=""):
        """Start monitoring with thread safety"""
        with self._lock:
            if self._monitoring_active:
                raise ValueError("Monitoring already active")
            
            # Validate interval bounds
            interval = max(MONITORING_CONFIG['min_interval'], 
                          min(interval, MONITORING_CONFIG['max_interval']))
            
            # Start monitoring thread
            self._monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                args=(interval, monitoring_type, prompt_style, custom_context),
                daemon=True
            )
            self._monitoring_thread.start()
            
            return True
    
    def _monitoring_loop(self, interval, monitoring_type, prompt_style, custom_context=""):
        """Main monitoring loop with immediate stop response"""
        
        # Set monitoring state
        session_id = hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        with self._lock:
            self._monitoring_active = True
            self._current_session_id = session_id
        
        ai_mode = "Real AI" if is_ai_enabled() else "Test Mode"
        logger.info(f"Starting responsive monitoring session: {session_id} with {ai_mode}")
        
        # Use API lock to capture baseline image immediately
        with self._api_lock:
            # Capture BASELINE image immediately when monitoring starts
            logger.info("Capturing baseline image immediately...")
            baseline_image = self.camera_service.capture_image()
            if not baseline_image:
                logger.error("Failed to capture baseline image")
                with self._lock:
                    self._monitoring_active = False
                return
            
            # Save baseline image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            baseline_path = f"{IMAGES_DIR}/baseline_{session_id}_{timestamp}.jpg"
            with open(baseline_path, 'wb') as f:
                f.write(baseline_image)
            
            with self._lock:
                self._baseline_image_path = baseline_path
            baseline_b64 = base64.b64encode(baseline_image).decode('utf-8')
            logger.info(f"Baseline established: {baseline_path}")
        
        capture_count = 0
        
        while self.is_active:
            try:
                capture_count += 1
                logger.info(f"Starting cycle #{capture_count} with video recording ({ai_mode})...")
                
                # Start video recording - this now returns immediately
                video_success = self.video_service.start_recording(interval, f"{session_id}_cycle_{capture_count}")
                
                if not video_success:
                    logger.error("Failed to start video recording")
                    time.sleep(2)
                    continue
                
                # Enhanced waiting with very frequent stop checking
                elapsed = 0
                check_interval = 0.1  # Check every 100ms
                
                while elapsed < interval and self.is_active:
                    time.sleep(check_interval)
                    elapsed += check_interval
                    
                    # Check for stop signal
                    if not self.is_active:
                        logger.info("Stop signal received - terminating monitoring immediately...")
                        self.video_service.stop_recording()
                        break
                
                if not self.is_active:
                    logger.info("Monitoring stopped by user request")
                    break
                
                logger.info(f"Cycle #{capture_count} - End of video recording period ({ai_mode})")
                
                # Use API lock for operations
                with self._api_lock:
                    # Stop current video recording and wait for completion
                    self.video_service.stop_recording()
                    
                    # Wait for video recording to complete with shorter timeout
                    video_completed = self.video_service.wait_for_completion(timeout=3.0)
                    if not video_completed:
                        logger.warning("Video recording did not complete within timeout")
                    
                    current_video_path = getattr(self.video_service, 'last_video_path', None)
                    
                    # Log video path for debugging
                    logger.info(f"Video recording completed: {current_video_path}")
                    if current_video_path and os.path.exists(current_video_path):
                        file_size = os.path.getsize(current_video_path)
                        logger.info(f"Video file confirmed: {file_size} bytes")
                    else:
                        logger.warning(f"Video file not found or invalid: {current_video_path}")
                    
                    # Capture current image
                    logger.info(f"Capturing analysis image (end of video period #{capture_count})...")
                    current_image = self.camera_service.capture_image()
                    if not current_image:
                        logger.warning("Failed to capture image, retrying...")
                        time.sleep(2)
                        continue
                    
                    # Save current image
                    current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    current_path = f"{IMAGES_DIR}/current_{session_id}_{current_timestamp}.jpg"
                    with open(current_path, 'wb') as f:
                        f.write(current_image)
                    
                    current_b64 = base64.b64encode(current_image).decode('utf-8')
                    
                    # Generate optimized prompt
                    prompt = PromptEngine.generate_optimized_prompt(
                        monitoring_type, prompt_style, custom_context
                    )
                    
                    # AI Analysis (works for both test and real mode)
                    logger.info(f"Performing AI analysis ({ai_mode})...")
                    ai_response = self.ai_service.analyze_images(baseline_b64, current_b64, prompt)
                    analysis_result = self.ai_service.parse_response(ai_response)
                    
                    # Log analysis results
                    logger.info(f"Analysis ({ai_mode}): {analysis_result['status']} "
                            f"({analysis_result['confidence']}% confidence, "
                            f"threat: {analysis_result['threat_level']})")
                    
                    # Save to database with video path
                    current_session = self.current_session_id
                    current_baseline = self.baseline_image_path
                    
                    self.db_manager.save_record(
                        current_session, current_baseline, current_path, 
                        monitoring_type, prompt_style, custom_context, 
                        prompt, ai_response, analysis_result, current_video_path
                    )
                    
                    # Log summary
                    if analysis_result['summary']:
                        logger.info(f"Summary ({ai_mode}): {analysis_result['summary']}")
                    
                    # Alert on high threat level
                    if analysis_result['threat_level'] >= AI_CONFIG['threat_level_threshold']:
                        logger.warning(f"HIGH THREAT DETECTED ({ai_mode}): Level {analysis_result['threat_level']}/10")
                        if current_video_path:
                            logger.info(f"Video recorded for threat analysis: {current_video_path}")
                    
                    # Send to Telegram
                    try:
                        current_timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.telegram_service.send_analysis_result(
                            analysis_result, current_session, monitoring_type,
                            current_baseline, current_path, current_timestamp_str, current_video_path
                        )
                    except Exception as telegram_error:
                        logger.error(f"Telegram notification failed: {telegram_error}")
                    
                    logger.info(f"Cycle #{capture_count} completed successfully - {analysis_result['status']}")
            
            except Exception as e:
                logger.error(f"Error in monitoring cycle #{capture_count} ({ai_mode}): {e}")
                # Stop current video recording on error
                self.video_service.stop_recording()
                time.sleep(2)
        
        # Final cleanup - ensure video recording is stopped
        self.video_service.stop_recording()
        logger.info(f"Monitoring session ended ({ai_mode}): {session_id}")
        
        with self._lock:
            self._monitoring_active = False
            self._current_session_id = None
            self._baseline_image_path = None

    def stop_monitoring(self):
        """Stop monitoring immediately with thread safety"""
        with self._lock:
            if self._monitoring_active:
                logger.info("Stopping monitoring immediately...")
                self._monitoring_active = False
                
                # Stop video recording immediately
                if hasattr(self, 'video_service'):
                    self.video_service.stop_recording()
                
                logger.info("Monitoring stop signal sent")
            else:
                logger.debug("No active monitoring to stop")

# Global monitoring service instance
_monitoring_service = None

def get_monitoring_service():
    """Get global monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service