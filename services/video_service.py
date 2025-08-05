"""
Video Recording Service
Manages video recording from ESP32-CAM with immediate stop capability
"""

import os
import time
import logging
import threading
import subprocess
from datetime import datetime
import cv2

try:
    from config import ESP32_CAM_CONFIG, STORAGE_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)

# Video Recording Configuration
VIDEO_CONFIG = {
    'fps': 20,
    'codec': 'MJPG',
    'quality': 80,
    'max_duration': 300,  # 5 minutes max
    'buffer_size': 1,
    'stop_check_interval': 0.05  # Check for stop signal every 50ms
}

class VideoRecordingService:
    """Video recording manager with immediate stop capability"""
    
    def __init__(self):
        self.is_recording = False
        self.video_writer = None
        self.video_frames = []
        self.frame_timestamps = []
        self.recording_start_time = None
        self.last_video_path = None
        self.current_video_path = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()  # For immediate stop signal
        self._recording_thread = None
        
    def start_recording(self, duration, session_id):
        """Start video recording with immediate stop capability"""
        with self._lock:
            try:
                if self.is_recording:
                    logger.warning("Recording already in progress")
                    return None
                    
                self.is_recording = True
                self._stop_event.clear()
                self.recording_start_time = time.time()
                
                logger.info(f"Starting video recording for {duration} seconds...")
                
                # Start recording in a separate thread that can be interrupted
                self._recording_thread = threading.Thread(
                    target=self._record_video_thread,
                    args=(duration, session_id),
                    daemon=True
                )
                self._recording_thread.start()
                
                return True  # Return immediately, actual path will be set later
                    
            except Exception as e:
                logger.error(f"Video recording error: {e}")
                self.is_recording = False
                return None
    
    def _record_video_thread(self, duration, session_id):
        """Internal video recording thread with immediate stop response"""
        try:
            # Clear previous data
            self.video_frames.clear()
            self.frame_timestamps.clear()
            
            # Setup video capture from ESP32-CAM
            stream_url = f"http://{ESP32_CAM_CONFIG['ip_address']}/stream"
            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                logger.error("Cannot open ESP32-CAM stream for recording")
                self.is_recording = False
                return
            
            # Configure capture settings for better quality
            cap.set(cv2.CAP_PROP_BUFFERSIZE, VIDEO_CONFIG['buffer_size'])
            cap.set(cv2.CAP_PROP_FPS, VIDEO_CONFIG['fps'])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
            
            # Enhanced recording loop with very frequent stop checking
            end_time = time.time() + duration
            frame_count = 0
            last_frame_time = time.time()
            frame_interval = 1.0 / VIDEO_CONFIG['fps']
            
            while time.time() < end_time and self.is_recording and not self._stop_event.is_set():
                current_time = time.time()
                
                # Check if it's time for next frame
                if current_time - last_frame_time >= frame_interval:
                    # Capture video frame
                    ret, frame = cap.read()
                    if ret:
                        recording_time = current_time - self.recording_start_time
                        self.video_frames.append(frame.copy())
                        self.frame_timestamps.append(recording_time)
                        frame_count += 1
                        last_frame_time = current_time
                
                # Check for stop signal very frequently
                time.sleep(VIDEO_CONFIG['stop_check_interval'])
            
            cap.release()
            
            # Log the reason for loop exit
            if self._stop_event.is_set():
                logger.info(f"Recording stopped by user request: {frame_count} frames captured")
            else:
                logger.info(f"Recording completed normally: {frame_count} frames")
            
            # Save video if we have frames
            if self.video_frames:
                video_path = self._save_video(session_id)
                self.last_video_path = video_path
                self.current_video_path = video_path
            else:
                logger.warning("No video frames captured")
                self.last_video_path = None
                
        except Exception as e:
            logger.error(f"Video recording thread error: {e}")
        finally:
            self.is_recording = False
    
    def stop_recording(self):
        """Stop current recording immediately"""
        with self._lock:
            if self.is_recording:
                logger.info("Stopping video recording immediately...")
                self._stop_event.set()
                self.is_recording = False
                
                # Wait for recording thread to finish with timeout
                if self._recording_thread and self._recording_thread.is_alive():
                    self._recording_thread.join(timeout=1.0)
                    if self._recording_thread.is_alive():
                        logger.warning("Video recording thread did not stop within timeout")
                    else:
                        logger.info("Video recording thread stopped successfully")
            else:
                logger.debug("No active recording to stop")
    
    def wait_for_completion(self, timeout=None):
        """Wait for current recording to complete"""
        with self._lock:
            if self._recording_thread and self._recording_thread.is_alive():
                self._recording_thread.join(timeout=timeout)
                return not self._recording_thread.is_alive()
            return True
    
    def _save_video(self, session_id):
        """Save recorded video"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_dir = os.path.join(STORAGE_CONFIG['images_directory'], 'videos')
            os.makedirs(video_dir, exist_ok=True)
            
            if not self.video_frames:
                logger.error("No video frames to save")
                return None
            
            # Get video properties
            height, width = self.video_frames[0].shape[:2]
            
            # Calculate actual FPS from timestamps
            if len(self.frame_timestamps) > 1:
                total_duration = max(self.frame_timestamps) - min(self.frame_timestamps)
                actual_fps = (len(self.frame_timestamps) - 1) / total_duration if total_duration > 0 else VIDEO_CONFIG['fps']
                actual_fps = max(5, min(int(actual_fps), 60))
            else:
                actual_fps = VIDEO_CONFIG['fps']
            
            # Create video file
            video_file = os.path.join(video_dir, f"video_{session_id}_{timestamp}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            out = cv2.VideoWriter(video_file, fourcc, actual_fps, (width, height))
            
            # Write video frames
            for frame in self.video_frames:
                out.write(frame)
            out.release()
            
            # Convert to MP4 format
            final_video_file = os.path.join(video_dir, f"video_{session_id}_{timestamp}.mp4")
            success = self._convert_to_mp4(video_file, final_video_file)
            
            if success:
                logger.info(f"Video saved successfully: {final_video_file}")
                return final_video_file
            else:
                logger.info(f"Video saved as AVI: {video_file}")
                return video_file
                
        except Exception as e:
            logger.error(f"Save video error: {e}")
            return None
    
    def _convert_to_mp4(self, input_file, output_file):
        """Convert video to MP4 format"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', input_file,
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-movflags', '+faststart',
                '-loglevel', 'warning',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                # Clean up temp file
                try:
                    os.remove(input_file)
                except:
                    pass
                logger.info("Video converted to MP4 successfully")
                return True
            else:
                logger.error(f"Video conversion failed: {result.stderr}")
                return False
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"FFmpeg not available or timeout: {e}")
            return False
        except Exception as e:
            logger.error(f"Video conversion error: {e}")
            return False
    
    def test_recording(self, duration=5):
        """Test video recording functionality"""
        test_session_id = "test_" + datetime.now().strftime('%H%M%S')
        return self.start_recording(duration, test_session_id)