#!/usr/bin/env python3
"""
Command Handlers for Telegram Bot
Handles all command-based interactions
"""

import os
import logging
import time
from datetime import datetime
from typing import Dict, Any

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..keyboards.main_menu import MainMenuKeyboards
from ..keyboards.monitoring_setup import MonitoringSetupKeyboards
from ..utils.message_formatter import MessageFormatter
from ..utils.validators import TelegramValidators

logger = logging.getLogger(__name__)

class CommandHandlers:
    """Handle Telegram bot commands"""
    
    def __init__(self, auth_service, monitoring_service, camera_service, user_sessions):
        """Initialize command handlers with services"""
        self.auth_service = auth_service
        self.monitoring_service = monitoring_service
        self.camera_service = camera_service
        self.user_sessions = user_sessions
        
        # Import configurations
        try:
            from config import ESP32_CAM_CONFIG, STORAGE_CONFIG, DATABASE_CONFIG, AVALAI_CONFIG, MONITORING_CONFIG
            self.esp32_config = ESP32_CAM_CONFIG
            self.storage_config = STORAGE_CONFIG
            self.database_config = DATABASE_CONFIG
            self.avalai_config = AVALAI_CONFIG
            self.monitoring_config = MONITORING_CONFIG
        except ImportError as e:
            logger.error(f"Failed to import configurations: {e}")
            raise
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = str(update.effective_user.id)
        
        if not self.auth_service.is_authorized(user_id):
            await update.message.reply_text(
                MessageFormatter.format_access_denied(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        welcome_message = MessageFormatter.format_welcome_message()
        reply_markup = MainMenuKeyboards.create_main_menu_keyboard()
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_id = str(update.effective_user.id)
        
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            elif update.callback_query:
                await update.callback_query.edit_message_text(MessageFormatter.format_access_denied())
            return
        
        help_text = MessageFormatter.format_help_message()
        keyboard = MainMenuKeyboards.create_back_to_main_keyboard()
        
        if update.message:
            await update.message.reply_text(
                help_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                help_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
    
    async def capture_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /capture command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._perform_capture(update, context)
    
    async def _perform_capture(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform image capture with proper error handling"""
        try:
            # Determine if this is from callback or direct message
            is_callback = update.callback_query is not None
            
            # Get chat_id first
            if is_callback:
                chat_id = update.callback_query.message.chat_id
                try:
                    await update.callback_query.delete_message()
                except:
                    pass
            else:
                chat_id = update.message.chat_id
            
            # Send status message
            status_message = await context.bot.send_message(
                chat_id=chat_id,
                text="📸 *Capturing image...*",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Capture image
            image_data = self.camera_service.capture_image()
            
            if not image_data:
                error_msg = "❌ *Failed to capture image*\n\nCamera may be offline or busy."
                reply_markup = MainMenuKeyboards.create_error_keyboard()
                await status_message.edit_text(error_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                return
            
            # Save temporary image
            temp_image_path = self.camera_service.save_temp_image(image_data, "telegram_capture")
            
            # Delete status message
            try:
                await status_message.delete()
            except:
                pass
            
            # Prepare caption and keyboard
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            caption = MessageFormatter.format_capture_result(
                timestamp, len(image_data), self.esp32_config['ip_address']
            )
            reply_markup = MainMenuKeyboards.create_capture_result_keyboard()
            
            # Send photo message
            with open(temp_image_path, 'rb') as photo_file:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
            # Clean up temp file
            self.camera_service.cleanup_temp_file(temp_image_path)
                
        except Exception as e:
            error_msg = MessageFormatter.format_error_message(str(e))
            reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=error_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except:
                pass
            logger.error(f"Capture error: {e}")
    
    async def video_test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /video_test command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._perform_video_test(update, context)
    
    async def _perform_video_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform video recording test"""
        try:
            # Import video service here to avoid circular imports
            from ..services.camera_service import VideoService
            video_service = VideoService(self.camera_service.main_app)
            
            # Determine if this is from callback or direct message
            is_callback = update.callback_query is not None
            
            # Get chat_id first
            if is_callback:
                chat_id = update.callback_query.message.chat_id
                try:
                    await update.callback_query.delete_message()
                except:
                    pass
            else:
                chat_id = update.message.chat_id
            
            # Send status message
            status_message = await context.bot.send_message(
                chat_id=chat_id,
                text="🎥 *Testing video recording...*\n\nRecording 10 second test video...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Start video recording using the main app's video service
            test_session_id = "telegram_test_" + datetime.now().strftime('%H%M%S')
            logger.info(f"Starting video test for session: {test_session_id}")
            
            # Use the main app's video recorder
            video_recorder = self.camera_service.main_app.video_recorder
            recording_success = video_recorder.start_recording(10, test_session_id)
            
            if not recording_success:
                error_msg = "❌ *Video test failed*\n\nFailed to start video recording."
                reply_markup = MainMenuKeyboards.create_error_keyboard()
                await status_message.edit_text(error_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                return
            
            # Update status to show recording in progress
            await status_message.edit_text(
                "🎥 *Recording in progress...*\n\n⏱️ Recording 10 seconds of video...\n📹 Please wait while video is being captured...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Wait for recording to complete with progress updates
            import asyncio
            wait_time = 0
            max_wait = 15  # 15 seconds timeout
            check_interval = 1  # Check every second
            
            while video_recorder.is_recording and wait_time < max_wait:
                await asyncio.sleep(check_interval)
                wait_time += check_interval
                
                # Update progress every 2 seconds
                if wait_time % 2 == 0 and wait_time <= 10:
                    await status_message.edit_text(
                        f"🎥 *Recording in progress...*\n\n⏱️ {wait_time}/10 seconds recorded\n📹 Video recording in progress...",
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            # Update status to processing
            await status_message.edit_text(
                "🎥 *Processing video recording...*\n\nEncoding and preparing video file for upload...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Wait a bit more for video processing
            await asyncio.sleep(2)
            
            # Get the video path
            video_path = getattr(video_recorder, 'last_video_path', None)
            
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                
                # Delete status message
                try:
                    await status_message.delete()
                except:
                    pass
                
                # Prepare caption and keyboard
                caption = MessageFormatter.format_video_test_result(file_size, self.esp32_config['ip_address'])
                reply_markup = MainMenuKeyboards.create_video_test_result_keyboard()
                
                # Send video if size is reasonable for Telegram
                if TelegramValidators.validate_file_size(file_size):
                    with open(video_path, 'rb') as video_file:
                        await context.bot.send_video(
                            chat_id=chat_id,
                            video=video_file,
                            caption=caption,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=reply_markup,
                            supports_streaming=True
                        )
                    
                    # Clean up test file after sending
                    try:
                        await asyncio.sleep(1)  # Brief delay before cleanup
                        os.remove(video_path)
                        logger.info(f"Cleaned up test video: {video_path}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup test video: {cleanup_error}")
                        
                else:
                    # File too large, send message only
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=caption + "\n\n⚠️ *Video file too large for Telegram upload*",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
            else:
                error_msg = "❌ *Video test failed*\n\nVideo recording completed but file not found or invalid."
                reply_markup = MainMenuKeyboards.create_error_keyboard()
                await status_message.edit_text(error_msg, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
                
        except Exception as e:
            error_msg = MessageFormatter.format_error_message(f"Video Test Error: {str(e)}")
            reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=error_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except:
                pass
            logger.error(f"Video test error: {e}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._show_status(update, context)
    
    async def _show_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system status"""
        try:
            # Get monitoring status
            status = self.monitoring_service.get_monitoring_status()
            monitoring_status = "🟢 Active" if status['active'] else "🔴 Inactive"
            session_id = status['session_id'] or "None"
            
            # Get camera info
            camera_info = self.camera_service.get_camera_info()
            camera_status = f"{camera_info['status_emoji']} {camera_info['status']}"
            
            # Get video status
            from ..services.camera_service import VideoService
            video_service = VideoService(self.camera_service.main_app)
            video_info = video_service.get_video_status()
            video_status = f"{video_info['status_emoji']} {video_info['status']}"
            
            # Get database record count
            try:
                records = self.monitoring_service.get_monitoring_history(1000)
                total_records = len(records)
                video_records = sum(1 for r in records if len(r) >= 17 and r[16])  # has_video column
            except Exception as db_error:
                logger.error(f"Database error in status: {db_error}")
                total_records = 0
                video_records = 0
            
            # Prepare status data
            status_data = {
                'monitoring_status': monitoring_status,
                'camera_status': camera_status,
                'video_status': video_status,
                'session_id': session_id,
                'total_records': total_records,
                'video_records': video_records,
                'camera_ip': self.esp32_config['ip_address'],
                'images_dir': self.storage_config['images_directory'],
                'videos_dir': f"{self.storage_config['images_directory']}/videos",
                'database': self.database_config['name'],
                'ai_model': self.avalai_config['model'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            status_text = MessageFormatter.format_system_status(status_data)
            reply_markup = MainMenuKeyboards.create_status_keyboard()
            
            if update.message:
                await update.message.reply_text(
                    status_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    status_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            error_message = MessageFormatter.format_error_message(f"Status Error: {str(e)}")
            try:
                if update.message:
                    await update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN)
                elif update.callback_query:
                    await update.callback_query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN)
            except:
                pass
            logger.error(f"Status error: {e}")
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._show_history(update, context)
    
    async def _show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show monitoring history"""
        try:
            # Get chat_id for consistent handling
            if update.callback_query:
                chat_id = update.callback_query.message.chat_id
                try:
                    await update.callback_query.delete_message()
                except:
                    pass
            else:
                chat_id = update.message.chat_id
            
            # Get records
            records = self.monitoring_service.get_monitoring_history(10)
            history_text = MessageFormatter.format_monitoring_history(records)
            reply_markup = MainMenuKeyboards.create_history_keyboard()
            
            # Always send new message for consistent behavior
            await context.bot.send_message(
                chat_id=chat_id,
                text=history_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            error_message = MessageFormatter.format_error_message(f"History Error: {str(e)}")
            reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            try:
                # Get chat_id for error handling
                if update.callback_query:
                    chat_id = update.callback_query.message.chat_id
                else:
                    chat_id = update.message.chat_id
                
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=error_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            except:
                pass
            
            logger.error(f"History error: {e}")
    
    async def monitor_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /monitor_start command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        # Check monitoring status
        status = self.monitoring_service.get_monitoring_status()
        if status['active']:
            message_text = "⚠️ *Monitoring Already Active*\n\nStop current session first."
            reply_markup = MonitoringSetupKeyboards.create_already_active_keyboard()
            
            if update.message:
                await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        # Initialize user session
        self.user_sessions[user_id] = {
            "monitoring_type": "security",
            "prompt_style": "formal", 
            "interval": 15,
            "custom_context": "",
            "step": "type_selection"
        }
        
        await self._show_monitoring_type_selection(update)
    
    async def _show_monitoring_type_selection(self, update: Update):
        """Show monitoring type selection menu"""
        text = MessageFormatter.format_monitoring_type_selection()
        reply_markup = MonitoringSetupKeyboards.create_monitoring_type_keyboard()
        
        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        except Exception as e:
            logger.error(f"Error showing monitoring type selection: {e}")
    
    async def monitor_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /monitor_stop command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._stop_monitoring_session(update, context)
    
    async def _stop_monitoring_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop monitoring session"""
        # Check monitoring status
        status = self.monitoring_service.get_monitoring_status()
        if not status['active']:
            message_text = "ℹ️ *No Active Monitoring*\n\nNo monitoring session is running."
            reply_markup = MonitoringSetupKeyboards.create_no_monitoring_keyboard()
            
            if update.message:
                await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return
        
        try:
            # Get session info for confirmation
            session_id = status['session_id'] or "Unknown"
            
            # Stop monitoring
            success = self.monitoring_service.stop_monitoring()
            
            if success:
                text = MessageFormatter.format_monitoring_stopped(session_id)
                reply_markup = MainMenuKeyboards.create_monitoring_stopped_keyboard()
            else:
                text = "❌ *Failed to Stop Monitoring*\n\nTry again or check system status."
                reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            if update.message:
                await update.message.reply_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
        except Exception as e:
            error_message = MessageFormatter.format_error_message(f"Stop Error: {str(e)}")
            reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            logger.error(f"Monitor stop error: {e}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            if update.message:
                await update.message.reply_text(MessageFormatter.format_access_denied())
            return
        
        await self._show_settings(update, context)
    
    async def _show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show system settings"""
        try:
            # Import additional config
            from config import TELEGRAM_CONFIG
            
            # Get video service status
            from ..services.camera_service import VideoService
            video_service = VideoService(self.camera_service.main_app)
            video_info = video_service.get_video_status()
            
            # Prepare config data
            config_data = {
                'camera_ip': self.esp32_config['ip_address'],
                'camera_timeout': self.esp32_config['timeout'],
                'camera_retry': self.esp32_config['retry_count'],
                'ai_model': self.avalai_config['model'],
                'ai_max_tokens': self.avalai_config['max_tokens'],
                'ai_temperature': self.avalai_config['temperature'],
                'default_interval': self.monitoring_config['default_interval'],
                'min_interval': self.monitoring_config['min_interval'],
                'max_interval': self.monitoring_config['max_interval'],
                'video_status': '🟢 Enabled' if hasattr(self.camera_service.main_app, 'video_recorder') else '❌ Disabled',
                'images_dir': self.storage_config['images_directory'],
                'videos_dir': f"{self.storage_config['images_directory']}/videos",
                'database': self.database_config['name'],
                'notifications_status': '✅ Enabled' if TELEGRAM_CONFIG['enabled'] else '❌ Disabled',
                'send_images_status': '✅ Yes' if TELEGRAM_CONFIG['send_images'] else '❌ No',
                'send_videos_status': '✅ Auto for threats' if TELEGRAM_CONFIG['enabled'] else '❌ Disabled'
            }
            
            settings_text = MessageFormatter.format_settings_message(config_data)
            reply_markup = MainMenuKeyboards.create_settings_keyboard()
            
            if update.message:
                await update.message.reply_text(
                    settings_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                await update.callback_query.edit_message_text(
                    settings_text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
        except Exception as e:
            error_message = MessageFormatter.format_error_message(f"Settings Error: {str(e)}")
            reply_markup = MainMenuKeyboards.create_error_keyboard()
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            logger.error(f"Settings error: {e}")