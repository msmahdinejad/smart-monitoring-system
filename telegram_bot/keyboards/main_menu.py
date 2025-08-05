#!/usr/bin/env python3
"""
Main Menu Keyboards for Telegram Bot
Handles main menu and navigation keyboard layouts
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class MainMenuKeyboards:
    """Handle main menu keyboard layouts"""
    
    @staticmethod
    def create_main_menu_keyboard():
        """Create enhanced main menu keyboard with Video Only features"""
        keyboard = [
            [
                InlineKeyboardButton("📸 Capture Image", callback_data="action_capture"),
                InlineKeyboardButton("📊 System Status", callback_data="action_status")
            ],
            [
                InlineKeyboardButton("▶️ Start Monitoring", callback_data="action_monitor_start"),
                InlineKeyboardButton("⏹️ Stop Monitoring", callback_data="action_monitor_stop")
            ],
            [
                InlineKeyboardButton("📋 View History", callback_data="action_history"),
                InlineKeyboardButton("🎥 Test Video", callback_data="action_video_test")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="action_settings"),
                InlineKeyboardButton("❓ Help", callback_data="action_help")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_back_to_main_keyboard():
        """Create simple back to main menu keyboard"""
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_error_keyboard():
        """Create error handling keyboard"""
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_capture_result_keyboard():
        """Create keyboard for capture result actions"""
        keyboard = [
            [InlineKeyboardButton("📸 Capture Another", callback_data="action_capture")],
            [InlineKeyboardButton("🎥 Test Video", callback_data="action_video_test")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_video_test_result_keyboard():
        """Create keyboard for video test result actions"""
        keyboard = [
            [InlineKeyboardButton("🎥 Test Again", callback_data="action_video_test")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_status_keyboard():
        """Create keyboard for status display"""
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="action_status"),
                InlineKeyboardButton("📸 Test Camera", callback_data="action_capture")
            ],
            [
                InlineKeyboardButton("🎥 Test Video Only", callback_data="action_video_test"),
                InlineKeyboardButton("📋 View History", callback_data="action_history")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_history_keyboard():
        """Create keyboard for history display"""
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="action_history")],
            [InlineKeyboardButton("🎥 Test Video Only", callback_data="action_video_test")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_settings_keyboard():
        """Create keyboard for settings display"""
        keyboard = [
            [InlineKeyboardButton("🎥 Test Video Only", callback_data="action_video_test")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_monitoring_control_keyboard():
        """Create keyboard for monitoring control"""
        keyboard = [
            [
                InlineKeyboardButton("⏹️ Stop Monitoring", callback_data="action_monitor_stop"),
                InlineKeyboardButton("📊 View Status", callback_data="action_status")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_monitoring_stopped_keyboard():
        """Create keyboard for when monitoring is stopped"""
        keyboard = [
            [
                InlineKeyboardButton("📋 View History", callback_data="action_history"),
                InlineKeyboardButton("▶️ Start New", callback_data="action_monitor_start")
            ],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)