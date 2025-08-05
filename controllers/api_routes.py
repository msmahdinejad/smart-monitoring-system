"""
API Routes Controller
Handles all API endpoints for the monitoring system
"""

import os
import time
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify

from services.monitoring_service import get_monitoring_service
from services.camera_service import CameraService
from services.video_service import VideoRecordingService
from services.telegram_service import TelegramService
from services.ai_service import AIAnalysisService
from models.database import DatabaseManager

try:
    from config import TELEGRAM_CONFIG, get_test_mode_status, AI_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

# Initialize services
monitoring_service = get_monitoring_service()
camera_service = CameraService()
video_service = VideoRecordingService()
telegram_service = TelegramService()
ai_service = AIAnalysisService()
db_manager = DatabaseManager()


@api_bp.route('/start', methods=['POST'])
def start_monitoring():
    """Start monitoring with thread safety"""
    try:
        if monitoring_service.is_active:
            return jsonify({"error": "Monitoring already active"})
        
        data = request.get_json()
        interval = int(data.get('interval', 30))
        monitoring_type = data.get('type', 'security')
        prompt_style = data.get('style', 'formal')
        custom_context = data.get('context', '')
        
        # Start monitoring
        success = monitoring_service.start_monitoring(
            interval, monitoring_type, prompt_style, custom_context
        )
        
        if success:
            return jsonify({"status": "started"})
        else:
            return jsonify({"error": "Failed to start monitoring"})
            
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        return jsonify({"error": str(e)})


@api_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """Stop monitoring with immediate response"""
    try:
        if not monitoring_service.is_active:
            return jsonify({
                "status": "not_active", 
                "message": "No active monitoring session to stop"
            })
        
        logger.info("Immediate stop request received")
        monitoring_service.stop_monitoring()
        
        # Brief wait to confirm stop with timeout
        max_wait = 3  # seconds
        wait_time = 0
        check_interval = 0.1
        
        while monitoring_service.is_active and wait_time < max_wait:
            time.sleep(check_interval)
            wait_time += check_interval
        
        if monitoring_service.is_active:
            logger.warning("Monitoring did not stop within timeout")
            return jsonify({
                "status": "timeout", 
                "message": "Stop request timed out - monitoring may still be stopping"
            })
        else:
            logger.info("Monitoring stopped successfully")
            return jsonify({
                "status": "stopped", 
                "message": "Monitoring stopped immediately"
            })
            
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        return jsonify({"status": "error", "error": str(e)})


@api_bp.route('/status')
def get_status():
    """Get current system status including test mode info"""
    try:
        telegram_status = telegram_service.enabled if telegram_service else False
    except:
        telegram_status = False
    
    state = monitoring_service.get_monitoring_state()
    test_mode_info = get_test_mode_status()
    
    return jsonify({
        "active": state['active'],
        "session_id": state['session_id'],
        "baseline_image": state['baseline_path'],
        "telegram_status": telegram_status,
        "video_recording": video_service.is_recording,
        "test_mode": test_mode_info,
        "ai_status": "Test Mode" if test_mode_info['test_mode'] else "Real AI",
        "config": {
            "camera_ip": camera_service.ip,
            "images_dir": "images",
            "video_enabled": True,
            "audio_enabled": False
        }
    })


@api_bp.route('/toggle-test-mode', methods=['POST'])
def toggle_test_mode():
    """Toggle between test mode and real AI"""
    try:
        data = request.get_json()
        enable_test = data.get('test_mode', True)
        
        # Update AI service
        ai_service.toggle_test_mode(enable_test)
        
        mode = "Test Mode" if enable_test else "Real AI"
        
        return jsonify({
            "success": True,
            "message": f"Switched to {mode}",
            "test_mode": enable_test,
            "ai_enabled": not enable_test
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })


@api_bp.route('/test-mode-info')
def get_test_mode_info():
    """Get detailed test mode information"""
    return jsonify(get_test_mode_status())


@api_bp.route('/records')
def get_records():
    """Get monitoring records with video support"""
    try:
        limit = request.args.get('limit', 50, type=int)
        records = db_manager.get_records(limit)
        
        records_list = []
        for record in records:
            # Handle both old and new database schemas
            if len(record) >= 17:  # New schema with video support
                records_list.append({
                    "id": record[0],
                    "timestamp": record[1],
                    "session_id": record[2],
                    "baseline_path": record[3],
                    "current_path": record[4],
                    "video_path": record[5],
                    "monitoring_type": record[6],
                    "prompt_style": record[7],
                    "custom_context": record[8] or "",
                    "prompt_used": record[9],
                    "ai_response": record[10],
                    "status": record[11],
                    "confidence": record[12],
                    "threat_level": record[13],
                    "summary": record[14] or "",
                    "keywords": record[15] or "",
                    "has_video": record[16] or False
                })
            else:  # Old schema compatibility
                records_list.append({
                    "id": record[0],
                    "timestamp": record[1],
                    "session_id": record[2],
                    "baseline_path": record[3],
                    "current_path": record[4],
                    "video_path": None,
                    "monitoring_type": record[5],
                    "prompt_style": record[6],
                    "custom_context": record[7] or "",
                    "prompt_used": record[8],
                    "ai_response": record[9],
                    "status": record[10],
                    "confidence": record[11],
                    "threat_level": record[12],
                    "summary": record[13] or "",
                    "keywords": record[14] or "",
                    "has_video": False
                })
        
        return jsonify(records_list)
        
    except Exception as e:
        logger.error(f"Error getting records: {e}")
        return jsonify({"error": str(e)})


@api_bp.route('/test-capture')
def test_capture():
    """Test camera capture"""
    try:
        image_data = camera_service.capture_image()
        if image_data:
            return jsonify({"success": True, "size": len(image_data)})
        else:
            return jsonify({"success": False, "error": "Camera connection failed"})
    except Exception as e:
        logger.error(f"Error testing camera: {e}")
        return jsonify({"success": False, "error": str(e)})


@api_bp.route('/test-telegram')
def test_telegram():
    """Test Telegram bot connection"""
    try:
        if not telegram_service.enabled:
            return jsonify({
                "success": False, 
                "error": "Telegram bot is disabled in configuration"
            })
        
        # Test connection
        success, message = telegram_service.test_connection()
        if not success:
            return jsonify({"success": False, "error": f"Connection failed: {message}"})
        
        # Send test message
        test_message = """🔧 <b>Test Message</b>

✅ Telegram Bot is working correctly!
🤖 Smart Monitoring System with Video Recording is ready.
🎥 Video recording will be sent for high threat levels.

<i>This is a test message from your enhanced monitoring system.</i>"""
        
        sent = telegram_service.send_message(test_message)
        
        if sent:
            return jsonify({
                "success": True, 
                "message": f"Test successful! {message}"
            })
        else:
            return jsonify({
                "success": False, 
                "error": "Failed to send test message"
            })
            
    except Exception as e:
        logger.error(f"Error testing Telegram: {e}")
        return jsonify({"success": False, "error": str(e)})


@api_bp.route('/test-video')
def test_video():
    """Test video recording functionality"""
    try:
        logger.info("Testing video recording...")
        
        # Test video recording for 5 seconds
        test_session_id = "test_" + datetime.now().strftime('%H%M%S')
        video_path = video_service.test_recording(5)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            return jsonify({
                "success": True,
                "message": f"Video test successful! File: {os.path.basename(video_path)}",
                "video_path": video_path,
                "file_size": file_size
            })
        else:
            return jsonify({
                "success": False,
                "error": "Video recording failed or file not created"
            })
            
    except Exception as e:
        logger.error(f"Video test error: {e}")
        return jsonify({
            "success": False,
            "error": f"Video test failed: {str(e)}"
        })


@api_bp.route('/camera-info')
def get_camera_info():
    """Get camera information and status"""
    try:
        is_connected = camera_service.test_connection()
        return jsonify({
            "success": True,
            "camera_ip": camera_service.ip,
            "stream_url": camera_service.get_stream_url(),
            "connected": is_connected,
            "timeout": camera_service.timeout,
            "retry_count": camera_service.retry_count
        })
    except Exception as e:
        logger.error(f"Error getting camera info: {e}")
        return jsonify({"success": False, "error": str(e)})


@api_bp.route('/system-info')
def get_system_info():
    """Get comprehensive system information"""
    try:
        # Get monitoring state
        monitoring_state = monitoring_service.get_monitoring_state()
        
        # Get camera status
        camera_connected = camera_service.test_connection()
        
        # Get Telegram status
        telegram_connected = False
        telegram_info = ""
        if telegram_service.enabled:
            telegram_connected, telegram_info = telegram_service.test_connection()
        
        # Get database stats
        records = db_manager.get_records(limit=1)
        total_records = len(db_manager.get_records(limit=1000))  # Rough estimate
        
        return jsonify({
            "success": True,
            "monitoring": {
                "active": monitoring_state['active'],
                "session_id": monitoring_state['session_id'],
                "baseline_path": monitoring_state['baseline_path']
            },
            "camera": {
                "connected": camera_connected,
                "ip": camera_service.ip,
                "stream_url": camera_service.get_stream_url()
            },
            "telegram": {
                "enabled": telegram_service.enabled,
                "connected": telegram_connected,
                "info": telegram_info
            },
            "video": {
                "recording": video_service.is_recording,
                "last_video": getattr(video_service, 'last_video_path', None)
            },
            "ai": {
                "test_mode": ai_service.test_mode,
                "enabled": ai_service.ai_enabled
            },
            "database": {
                "path": db_manager.db_path,
                "recent_records": len(records),
                "estimated_total": total_records
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({"success": False, "error": str(e)})


@api_bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "monitoring": monitoring_service.is_active,
                "camera": camera_service.test_connection(),
                "video": not video_service.is_recording,  # True when not recording (available)
                "telegram": telegram_service.enabled,
                "database": os.path.exists(db_manager.db_path)
            }
        })
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })