#!/usr/bin/env python3
"""
Message Handlers for Telegram Bot
Handles text message interactions
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from ..keyboards.monitoring_setup import MonitoringSetupKeyboards
from ..utils.message_formatter import MessageFormatter
from ..utils.validators import TelegramValidators

logger = logging.getLogger(__name__)

class MessageHandlers:
    """Handle Telegram bot text messages"""
    
    def __init__(self, auth_service, user_sessions):
        """Initialize message handlers with services"""
        self.auth_service = auth_service
        self.user_sessions = user_sessions
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages for context input"""
        user_id = str(update.effective_user.id)
        
        # Check authorization
        if not self.auth_service.is_authorized(user_id):
            await update.message.reply_text(
                MessageFormatter.format_access_denied(),
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if user has an active session
        if user_id not in self.user_sessions:
            await self._handle_no_session(update, context)
            return
        
        session = self.user_sessions[user_id]
        
        # Handle based on session step
        if session.get("step") == "awaiting_context":
            await self._handle_context_input(update, context, user_id, session)
        else:
            await self._handle_unexpected_message(update, context)
    
    async def _handle_context_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, session: dict):
        """Handle custom context input from user"""
        try:
            # Get and validate user input
            user_input = update.message.text.strip()
            sanitized_input = TelegramValidators.sanitize_text_input(user_input, max_length=500)
            
            if not TelegramValidators.validate_custom_context(sanitized_input):
                await update.message.reply_text(
                    "❌ *Invalid Input*\n\n"
                    "Please provide a valid context (1-500 characters).\n\n"
                    "*Examples:*\n"
                    "• 'Monitor for fire or smoke detection'\n"
                    "• 'Check if the printer is working properly'\n"
                    "• 'Detect package deliveries at the door'\n"
                    "• 'Monitor pet activity and behavior'\n\n"
                    "Try again or send /start to go back.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Save custom context
            session["custom_context"] = sanitized_input
            session["step"] = "context_input"
            
            # Send confirmation message
            await update.message.reply_text(
                f"✅ *Custom Focus Added*\n\n"
                f"Your specific focus: `{sanitized_input}`\n\n"
                f"The AI will now pay special attention to this requirement during monitoring.\n"
                f"🎥 Video recording will also focus on these specified areas.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Show enhanced summary with ready to start options
            await self._show_enhanced_summary(update, context, user_id, session, sanitized_input)
            
        except Exception as e:
            logger.error(f"Error handling context input: {e}")
            await update.message.reply_text(
                MessageFormatter.format_error_message(f"Error processing your input: {str(e)}"),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _show_enhanced_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, session: dict, context_text: str):
        """Show enhanced monitoring configuration summary"""
        try:
            # Import services to avoid circular imports
            from ..services.monitoring_service import MonitoringService
            monitoring_service = MonitoringService(None)  # We only need the static data
            
            monitoring_types = monitoring_service.get_monitoring_types()
            prompt_styles = monitoring_service.get_prompt_styles()
            
            type_name = monitoring_types[session["monitoring_type"]].split('\n')[0]
            style_name = prompt_styles[session["prompt_style"]].split('\n')[0]
            interval = session["interval"]
            
            text = f"""🎯 *Enhanced Monitoring Configuration*

*Base Type:* {type_name}
*Analysis Style:* {style_name}
*Check Interval:* {interval} seconds
*Video Duration:* {interval} seconds per session
*Custom Focus:* {context_text}

🤖 The AI will now combine the base monitoring type with your specific focus for more precise analysis.
🎥 Video recording will capture {interval}-second clips during each monitoring cycle.

Ready to start your customized monitoring?"""

            keyboard = MonitoringSetupKeyboards.create_context_editing_keyboard()
            
            await update.message.reply_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
        except Exception as e:
            logger.error(f"Error showing enhanced summary: {e}")
            await update.message.reply_text(
                MessageFormatter.format_error_message(f"Error displaying configuration: {str(e)}"),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _handle_no_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle message when user has no active session"""
        await update.message.reply_text(
            "ℹ️ *No Active Setup*\n\n"
            "You don't have an active monitoring setup session.\n\n"
            "Use /start to begin or /help for available commands.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start Setup", callback_data="action_monitor_start")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
            ])
        )
    
    async def _handle_unexpected_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unexpected text messages"""
        await update.message.reply_text(
            "🤔 *Unexpected Message*\n\n"
            "I'm not sure what you're trying to do right now.\n\n"
            "Use /start for the main menu or /help for available commands.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")],
                [InlineKeyboardButton("❓ Help", callback_data="action_help")]
            ])
        )
    
    async def handle_session_timeout(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
        """Handle session timeout scenario"""
        # Clean up timed out session
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        await update.message.reply_text(
            "⏰ *Session Timeout*\n\n"
            "Your monitoring setup session has expired.\n\n"
            "Please start over to configure monitoring.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Start New Setup", callback_data="action_monitor_start")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
            ])
        )
    
    def cleanup_user_session(self, user_id: str):
        """Clean up user session data"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            logger.info(f"Cleaned up session for user: {user_id}")
    
    def get_user_session(self, user_id: str) -> dict:
        """Get user session data"""
        return self.user_sessions.get(user_id, {})
    
    def has_active_session(self, user_id: str) -> bool:
        """Check if user has active session"""
        return user_id in self.user_sessions
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.user_sessions)