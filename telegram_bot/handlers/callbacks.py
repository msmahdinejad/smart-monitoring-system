#!/usr/bin/env python3
"""
Callback Handlers for Telegram Bot
Handles all callback query interactions
"""

import logging
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

class CallbackHandlers:
    """Handle Telegram bot callback queries"""
    
    def __init__(self, auth_service, monitoring_service, camera_service, user_sessions):
        """Initialize callback handlers with services"""
        self.auth_service = auth_service
        self.monitoring_service = monitoring_service
        self.camera_service = camera_service
        self.user_sessions = user_sessions
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        
        user_id = str(update.effective_user.id)
        if not self.auth_service.is_authorized(user_id):
            await query.answer("❌ Access denied.")
            return
        
        data = query.data
        
        # Validate callback data
        if not TelegramValidators.validate_callback_data(data):
            await query.answer("❌ Invalid callback data.")
            logger.warning(f"Invalid callback data: {data}")
            return
        
        # Answer the callback query immediately
        await query.answer()
        
        try:
            # Route callback to appropriate handler
            if data.startswith("action_"):
                await self._handle_action_callback(update, context, data)
            elif data.startswith("montype_"):
                await self._handle_monitoring_type_callback(update, context, data, user_id)
            elif data.startswith("style_"):
                await self._handle_style_callback(update, context, data, user_id)
            elif data.startswith("interval_"):
                await self._handle_interval_callback(update, context, data, user_id)
            elif data.startswith("nav_"):
                await self._handle_navigation_callback(update, context, data, user_id)
            else:
                logger.warning(f"Unhandled callback data: {data}")
            
        except Exception as e:
            await self._handle_callback_error(update, context, e)
    
    async def _handle_action_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle action callbacks"""
        # Import command handlers to avoid circular imports
        from .commands import CommandHandlers
        command_handlers = CommandHandlers(
            self.auth_service,
            self.monitoring_service,
            self.camera_service,
            self.user_sessions
        )
        
        action = data.replace("action_", "")
        
        if action == "main_menu":
            await self._send_main_menu(update, context, edit_message=True)
        elif action == "capture":
            await command_handlers._perform_capture(update, context)
        elif action == "video_test":
            await command_handlers._perform_video_test(update, context)
        elif action == "status":
            await command_handlers._show_status(update, context)
        elif action == "history":
            await command_handlers._show_history(update, context)
        elif action == "monitor_start":
            await command_handlers.monitor_start_command(update, context)
        elif action == "monitor_stop":
            await command_handlers._stop_monitoring_session(update, context)
        elif action == "settings":
            await command_handlers._show_settings(update, context)
        elif action == "help":
            await command_handlers.help_command(update, context)
        elif action == "add_context":
            await self._handle_add_context(update, context)
        elif action == "start_monitoring":
            await self._start_monitoring_session(update, context)
        else:
            logger.warning(f"Unhandled action: {action}")
    
    async def _handle_monitoring_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, user_id: str):
        """Handle monitoring type selection callback"""
        monitoring_type = data.replace("montype_", "")
        
        if not TelegramValidators.validate_monitoring_type(monitoring_type):
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message("Invalid monitoring type"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Initialize or update user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "monitoring_type": "security",
                "prompt_style": "formal", 
                "interval": 15,
                "custom_context": "",
                "step": "type_selection"
            }
        
        self.user_sessions[user_id]["monitoring_type"] = monitoring_type
        self.user_sessions[user_id]["step"] = "style_selection"
        await self._show_prompt_style_selection(update, user_id)
    
    async def _handle_style_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, user_id: str):
        """Handle prompt style selection callback"""
        style = data.replace("style_", "")
        
        if not TelegramValidators.validate_prompt_style(style):
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message("Invalid prompt style"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["prompt_style"] = style
            self.user_sessions[user_id]["step"] = "interval_selection"
            await self._show_interval_selection(update, user_id)
    
    async def _handle_interval_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, user_id: str):
        """Handle interval selection callback"""
        try:
            interval = int(data.replace("interval_", ""))
        except ValueError:
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message("Invalid interval format"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if not TelegramValidators.validate_interval(interval):
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message("Invalid interval value"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["interval"] = interval
            self.user_sessions[user_id]["step"] = "context_input"
            await self._show_context_input(update, user_id)
    
    async def _handle_navigation_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, user_id: str):
        """Handle navigation callbacks"""
        nav_action = data.replace("nav_", "")
        
        if nav_action == "style_selection" and user_id in self.user_sessions:
            await self._show_prompt_style_selection(update, user_id)
        elif nav_action == "interval_selection" and user_id in self.user_sessions:
            await self._show_interval_selection(update, user_id)
        else:
            logger.warning(f"Unhandled navigation: {nav_action}")
    
    async def _send_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, edit_message=True):
        """Send or edit main menu"""
        welcome_message = MessageFormatter.format_welcome_message()
        reply_markup = MainMenuKeyboards.create_main_menu_keyboard()
        
        try:
            if edit_message and update.callback_query:
                await update.callback_query.edit_message_text(
                    welcome_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            else:
                # Send new message
                if update.callback_query:
                    await update.callback_query.message.reply_text(
                        welcome_message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                elif update.message:
                    await update.message.reply_text(
                        welcome_message,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
        except Exception as e:
            logger.error(f"Error sending main menu: {e}")
            # Fallback: send new message
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    welcome_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
    
    async def _show_prompt_style_selection(self, update: Update, user_id: str):
        """Show prompt style selection menu"""
        session = self.user_sessions[user_id]
        selected_type = session["monitoring_type"]
        
        # Get monitoring types from service
        monitoring_types = self.monitoring_service.get_monitoring_types()
        type_name = monitoring_types[selected_type].split('\n')[0]
        
        role_descriptions = {
            "security": "👮‍♂️ Security Guard",
            "presence": "🏢 Facility Supervisor", 
            "lighting": "⚡ Electrical Technician",
            "classroom": "👨‍🏫 Teacher",
            "workplace": "🦺 Safety Officer",
            "custom": "🎯 Custom Professional"
        }
        
        role_desc = role_descriptions.get(selected_type, type_name)
        text = MessageFormatter.format_prompt_style_selection(role_desc)
        reply_markup = MonitoringSetupKeyboards.create_prompt_style_keyboard()
        
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _show_interval_selection(self, update: Update, user_id: str):
        """Show interval selection menu"""
        session = self.user_sessions[user_id]
        
        # Get monitoring types and styles from service
        monitoring_types = self.monitoring_service.get_monitoring_types()
        prompt_styles = self.monitoring_service.get_prompt_styles()
        
        type_name = monitoring_types[session["monitoring_type"]].split('\n')[0]
        style_name = prompt_styles[session["prompt_style"]].split('\n')[0]
        
        text = MessageFormatter.format_interval_selection(type_name, style_name)
        reply_markup = MonitoringSetupKeyboards.create_interval_selection_keyboard()
        
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _show_context_input(self, update: Update, user_id: str):
        """Show context input option"""
        session = self.user_sessions[user_id]
        
        # Get monitoring types and styles from service
        monitoring_types = self.monitoring_service.get_monitoring_types()
        prompt_styles = self.monitoring_service.get_prompt_styles()
        
        type_name = monitoring_types[session["monitoring_type"]].split('\n')[0]
        style_name = prompt_styles[session["prompt_style"]].split('\n')[0]
        interval = session["interval"]
        
        # Get monitoring type description
        monitoring_descriptions = {
            "security": "🔒 Will monitor for unauthorized access, theft, intrusion, suspicious activities",
            "presence": "👥 Will detect human presence, movement patterns, occupancy changes",
            "lighting": "💡 Will monitor electrical devices, lighting changes, power status",
            "classroom": "🎓 Will analyze student engagement, educational environment, activities",
            "workplace": "🏢 Will monitor workplace safety, productivity, compliance",
            "custom": "⚙️ Will use your custom requirements for monitoring"
        }
        
        monitoring_desc = monitoring_descriptions.get(session["monitoring_type"], "")
        text = MessageFormatter.format_context_input(type_name, style_name, interval, monitoring_desc)
        reply_markup = MonitoringSetupKeyboards.create_context_input_keyboard()
        
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def _handle_add_context(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle add custom context request"""
        user_id = str(update.effective_user.id)
        
        if user_id in self.user_sessions:
            self.user_sessions[user_id]["step"] = "awaiting_context"
            await update.callback_query.edit_message_text(
                """📝 *Add Custom Context*

Please type your specific monitoring instructions.

*Examples:*
• 'Monitor for fire or smoke detection'
• 'Check if the printer is working properly'  
• 'Detect package deliveries at the door'
• 'Monitor computer screens for activity'
• 'Check for water leaks or flooding'
• 'Detect if windows or doors are open'
• 'Monitor pet activity and behavior'
• 'Check for equipment malfunction signs'

*Write naturally* - describe what you want the AI to watch for.

🎥 Video recording will focus on your specified areas.

Send /start to go back.""",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _start_monitoring_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start monitoring with user's configuration and video recording"""
        user_id = str(update.effective_user.id)
        
        if user_id not in self.user_sessions:
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message("Session not found. Please start over."),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        session = self.user_sessions[user_id]
        
        # Validate session configuration
        is_valid, error_msg = TelegramValidators.validate_session_config(session)
        if not is_valid:
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message(f"Configuration Error: {error_msg}"),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        try:
            # Check if monitoring is already active
            status = self.monitoring_service.get_monitoring_status()
            if status['active']:
                await update.callback_query.edit_message_text(
                    "❌ *Monitoring Already Active*\n\nPlease stop current session first.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Start monitoring using service
            success = self.monitoring_service.start_monitoring(
                session["interval"],
                session["monitoring_type"],
                session["prompt_style"],
                session["custom_context"]
            )
            
            if not success:
                await update.callback_query.edit_message_text(
                    "❌ *Failed to Start Monitoring*\n\nCheck system status and try again.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Success message
            monitoring_types = self.monitoring_service.get_monitoring_types()
            prompt_styles = self.monitoring_service.get_prompt_styles()
            
            type_name = monitoring_types[session["monitoring_type"]].split('\n')[0]
            style_name = prompt_styles[session["prompt_style"]].split('\n')[0]
            
            monitoring_descriptions = {
                "security": "🔒 Now monitoring for security threats with video recording",
                "presence": "👥 Now detecting human presence with video activity recording",
                "lighting": "💡 Now monitoring electrical devices with video status recording",
                "classroom": "🎓 Now analyzing educational environment with video session recording",
                "workplace": "🏢 Now monitoring workplace safety with video compliance recording",
                "custom": "⚙️ Now monitoring based on your custom requirements with video"
            }
            
            monitoring_desc = monitoring_descriptions.get(session["monitoring_type"], "")
            
            # Prepare configuration data for formatter
            config_data = {
                'type_name': type_name,
                'style_name': style_name,
                'interval': session['interval'],
                'custom_context': session.get('custom_context', ''),
                'monitoring_desc': monitoring_desc,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            success_text = MessageFormatter.format_monitoring_started(config_data)
            reply_markup = MainMenuKeyboards.create_monitoring_control_keyboard()
            
            await update.callback_query.edit_message_text(
                success_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Clean up user session
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
            
        except Exception as e:
            await update.callback_query.edit_message_text(
                MessageFormatter.format_error_message(f"Failed to Start Monitoring: {str(e)}"),
                parse_mode=ParseMode.MARKDOWN
            )
            logger.error(f"Start monitoring error: {e}")
    
    async def _handle_callback_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
        """Handle callback errors"""
        error_keyboard = MainMenuKeyboards.create_error_keyboard()
        error_msg = MessageFormatter.format_error_message(str(error))
        
        try:
            # Try to edit first
            await update.callback_query.edit_message_text(
                error_msg,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=error_keyboard
            )
        except:
            # If edit fails, send new message
            try:
                await context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=error_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=error_keyboard
                )
            except:
                pass
        
        logger.error(f"Callback error: {error}")