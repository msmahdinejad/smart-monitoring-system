#!/usr/bin/env python3
"""
Smart Monitoring System with Video Recording
Main entry point for the application
"""

import os
import sys
import subprocess
import logging
from utils.logging_setup import setup_logging
from utils.directory_setup import create_directories
from models.database import DatabaseManager
from services.camera_service import CameraService
from services.telegram_service import TelegramService
from services.monitoring_service import get_monitoring_service
from services.video_service import VideoRecordingService
from services.ai_service import AIAnalysisService
from app import create_app

# Import configuration
try:
    from config import (
        ESP32_CAM_CONFIG, TELEGRAM_CONFIG, SERVER_CONFIG, 
        validate_config, display_config, IMAGES_DIR
    )
except ImportError:
    print("❌ ERROR: config.py not found!")
    sys.exit(1)

# Initialize logger
logger = logging.getLogger(__name__)


def create_main_app_instance():
    """Create MainApplication instance for telegram_bot.py compatibility"""
    class MainApplication:
        def __init__(self):
            self.camera = CameraService()
            self.DatabaseManager = DatabaseManager  # Class reference
            self.db_manager = DatabaseManager()     # Instance for direct use
            self.monitoring_service = get_monitoring_service()
            self.video_recorder = VideoRecordingService()
            self.ai_service = AIAnalysisService()
            
            # Add config references for compatibility
            from config import AVALAI_CONFIG
            self.AVALAI_CONFIG = AVALAI_CONFIG
            
            # Add monitoring functions for compatibility with telegram_bot.py
            self.api_lock = self.monitoring_service._api_lock
            self.get_monitoring_state = self.monitoring_service.get_monitoring_state
            
            # Compatibility wrapper for set_monitoring_state
            def set_monitoring_state(**kwargs):
                if kwargs.get('active') == False:
                    self.monitoring_service.stop_monitoring()
            self.set_monitoring_state = set_monitoring_state
            
            # Compatibility wrapper for monitoring_loop
            def monitoring_loop(interval, monitoring_type, prompt_style, custom_context=""):
                try:
                    return self.monitoring_service.start_monitoring(
                        interval, monitoring_type, prompt_style, custom_context
                    )
                except Exception as e:
                    logger.error(f"Monitoring loop wrapper error: {e}")
                    return False
            self.monitoring_loop = monitoring_loop
    
    return MainApplication()


def initialize_enhanced_telegram_bot(main_app_instance):
    """Initialize Enhanced Telegram Bot from external telegram_bot.py"""
    try:
        from telegram_bot import create_telegram_bot
        telegram_bot_instance = create_telegram_bot(main_app_instance)
        
        if telegram_bot_instance:
            # Start bot in background thread
            bot_thread = telegram_bot_instance.run_bot_async()
            print("✅ Enhanced Telegram Bot started successfully")
            print("🤖 Bot features: /start for full menu, instant capture, monitoring control")
            print("🎥 Bot will send videos for high-threat detections")
            return telegram_bot_instance
        else:
            print("⚠️ Enhanced Telegram Bot not started (disabled or misconfigured)")
            return None
            
    except ImportError:
        print("⚠️ Enhanced Telegram Bot module not found (telegram_bot.py)")
        print("   Basic notifications will still work")
        return None
    except Exception as e:
        print(f"⚠️ Enhanced Telegram Bot failed to start: {e}")
        print("   Basic notifications will still work")
        return None


def test_system_components():
    """Test all system components during startup"""
    # Test camera connection
    camera_service = CameraService()
    if camera_service.test_connection():
        print(f"✅ Camera connected: {ESP32_CAM_CONFIG['ip_address']}")
    else:
        print(f"⚠️ Camera not responding: {ESP32_CAM_CONFIG['ip_address']}")
        print("   System will continue, but monitoring may fail.")
    
    # Test video recording components
    print("🎥 Testing video recording components...")
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg detected for video processing")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ FFmpeg not found - videos will be basic format only")
    
    # Test Telegram bot connection
    telegram_service = TelegramService()
    if TELEGRAM_CONFIG['enabled']:
        success, message = telegram_service.test_connection()
        if success:
            print(f"✅ Telegram Bot: {message}")
            print("📹 Video notifications will be sent for high threat levels")
        else:
            print(f"⚠️ Telegram Bot: {message}")
            print("   Check bot token and configuration.")
    else:
        print("📱 Telegram notifications: Disabled")


def main():
    """Main application entry point"""
    print("🚀 Starting Enhanced Smart Monitoring System with Video Recording...")
    print("=" * 70)
    
    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        print("❌ Configuration Errors:")
        for error in config_errors:
            print(f"   {error}")
        if any("API_KEY" in error for error in config_errors):
            print("\n💡 Please update config.py with your API key before running!")
            sys.exit(1)
    
    # Display configuration
    display_config()
    print("=" * 70)
    
    # Setup logging
    logger = setup_logging()
    
    # Create required directories
    create_directories()
    
    # Initialize database
    db_manager = DatabaseManager()
    db_manager.init_database()
    
    # Test system components
    test_system_components()
    
    # Create Flask app
    app = create_app()
    
    # Create MainApplication instance for telegram_bot.py compatibility
    main_app_instance = create_main_app_instance()
    
    # Initialize Enhanced Telegram Bot (from external telegram_bot.py)
    telegram_bot_instance = initialize_enhanced_telegram_bot(main_app_instance)
    
    print(f"🗄️ Database: {db_manager.db_path}")
    print(f"📁 Images directory: {IMAGES_DIR}")
    print(f"🎬 Videos directory: {os.path.join(IMAGES_DIR, 'videos')}")
    print(f"🌐 Starting web server...")
    print(f"📱 Web Interface: http://localhost:{SERVER_CONFIG['port']}")
    
    if TELEGRAM_CONFIG['enabled']:
        print(f"🤖 Telegram Bot: Enhanced bot with video support")
        print("   Send /start to your bot for full control menu")
        print("   Videos automatically sent for threat level ≥ 5")
    
    print("=" * 70)
    print("🎥 VIDEO RECORDING FEATURES:")
    print("   • Automatic recording during each monitoring interval")
    print("   • Video sent via Telegram for high threat levels")
    print("   • FFmpeg processing for optimal quality")
    print("   • Complete history with video playback")
    print("=" * 70)
    
    try:
        app.run(
            host=SERVER_CONFIG['host'], 
            port=SERVER_CONFIG['port'], 
            debug=SERVER_CONFIG['debug'],
            threaded=SERVER_CONFIG['threaded']
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        monitoring_service = get_monitoring_service()
        monitoring_service.stop_monitoring()
        try:
            if 'telegram_bot_instance' in locals() and telegram_bot_instance:
                print("🤖 Stopping Enhanced Telegram bot...")
        except:
            pass
    except Exception as e:
        logger = setup_logging()
        logger.error(f"Server error: {e}")
        print(f"❌ Server error: {e}")


if __name__ == '__main__':
    main()