#!/usr/bin/env python3
"""
Main Telegram Bot Class - Clean Architecture Implementation
Enhanced Telegram Bot for Smart Environmental Monitoring System - Video Only
"""

import asyncio
import threading
import logging
from typing import Dict, Any, Optional

# Telegram Bot imports
try:
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
except ImportError:
    print("ERROR: python-telegram-bot library not found!")
    print("Please install: pip install python-telegram-bot")
    exit(1)

# Import handlers
from .handlers.commands import CommandHandlers
from .handlers.callbacks import CallbackHandlers
from .handlers.messages import MessageHandlers

# Import services
from .services.auth_service import AuthService
from .services.monitoring_service import MonitoringService
from .services.camera_service import CameraService

logger = logging.getLogger(__name__)

class TelegramMonitoringBot:
    """Enhanced Telegram bot with Video Only recording support (no Arduino audio)"""
    
    def __init__(self, main_app_instance):
        """Initialize bot with reference to main application instance"""
        try:
            from config import TELEGRAM_CONFIG
        except ImportError:
            raise Exception("Failed to import TELEGRAM_CONFIG from config.py")
        
        self.main_app = main_app_instance
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        
        # Initialize services
        self.auth_service = AuthService(TELEGRAM_CONFIG)
        self.monitoring_service = MonitoringService(main_app_instance)
        self.camera_service = CameraService(main_app_instance)
        
        # User session data for monitoring setup
        self.user_sessions = {}
        
        # Initialize application
        self.application = None
        self.setup_bot()
    
    def setup_bot(self):
        """Setup bot application and handlers"""
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Initialize handlers with services
            command_handlers = CommandHandlers(
                self.auth_service, 
                self.monitoring_service, 
                self.camera_service,
                self.user_sessions
            )
            
            callback_handlers = CallbackHandlers(
                self.auth_service,
                self.monitoring_service,
                self.camera_service,
                self.user_sessions
            )
            
            message_handlers = MessageHandlers(
                self.auth_service,
                self.user_sessions
            )
            
            # Register command handlers
            self.application.add_handler(CommandHandler("start", command_handlers.start_command))
            self.application.add_handler(CommandHandler("help", command_handlers.help_command))
            self.application.add_handler(CommandHandler("capture", command_handlers.capture_command))
            self.application.add_handler(CommandHandler("status", command_handlers.status_command))
            self.application.add_handler(CommandHandler("history", command_handlers.history_command))
            self.application.add_handler(CommandHandler("monitor_start", command_handlers.monitor_start_command))
            self.application.add_handler(CommandHandler("monitor_stop", command_handlers.monitor_stop_command))
            self.application.add_handler(CommandHandler("settings", command_handlers.settings_command))
            self.application.add_handler(CommandHandler("video_test", command_handlers.video_test_command))
            
            # Register callback query handler
            self.application.add_handler(CallbackQueryHandler(callback_handlers.handle_callback))
            
            # Register message handler for custom context input
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                message_handlers.handle_text_message
            ))
            
            logger.info("Enhanced Telegram bot handlers registered successfully (Video Only)")
            
        except Exception as e:
            logger.error(f"Failed to setup Telegram bot: {e}")
            raise
    
    def run_bot_async(self):
        """Run the bot in a separate thread"""
        def bot_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                logger.info("Starting enhanced Telegram bot with Video Only support...")
                self.application.run_polling(
                    drop_pending_updates=True,
                    allowed_updates=["message", "callback_query"]
                )
            except Exception as e:
                logger.error(f"Bot thread error: {e}")
        
        thread = threading.Thread(target=bot_thread, daemon=True)
        thread.start()
        logger.info("Enhanced Telegram bot started in background thread (Video Only)")
        return thread