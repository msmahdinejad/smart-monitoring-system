#!/usr/bin/env python3
"""
Monitoring Setup Keyboards for Telegram Bot
Handles monitoring configuration keyboard layouts
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class MonitoringSetupKeyboards:
    """Handle monitoring setup keyboard layouts"""
    
    @staticmethod
    def create_monitoring_type_keyboard():
        """Create monitoring type selection keyboard"""
        monitoring_types = [
            ("security", "🔒 Security Guard"),
            ("presence", "👥 Facility Supervisor"),
            ("lighting", "💡 Electrical Technician"),
            ("classroom", "🎓 Teacher & Supervisor"),
            ("workplace", "🏢 Safety Officer"),
            ("custom", "⚙️ Custom Professional")
        ]
        
        keyboard = []
        for key, title in monitoring_types:
            keyboard.append([InlineKeyboardButton(title, callback_data=f"montype_{key}")])
        
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_prompt_style_keyboard():
        """Create prompt style selection keyboard"""
        prompt_styles = [
            ("formal", "📋 Official Report"),
            ("technical", "🔧 Expert Technical"),
            ("casual", "💬 Friendly Colleague"),
            ("security", "🚨 Security Professional"),
            ("report", "📊 Executive Briefing")
        ]
        
        keyboard = []
        for key, title in prompt_styles:
            keyboard.append([InlineKeyboardButton(title, callback_data=f"style_{key}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="action_monitor_start")])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_interval_selection_keyboard():
        """Create interval selection keyboard"""
        intervals = [
            ("5", "⚡ 5 seconds - Very Fast + 5s Video"),
            ("15", "🔄 15 seconds - Recommended + 15s Video"),
            ("30", "⏱️ 30 seconds - Regular + 30s Video"),
            ("60", "🕐 1 minute - Periodic + 1min Video"),
            ("120", "🕑 2 minutes - Slow + 2min Video"),
            ("300", "🕔 5 minutes - Very Slow + 5min Video")
        ]
        
        keyboard = []
        for interval, label in intervals:
            keyboard.append([InlineKeyboardButton(label, callback_data=f"interval_{interval}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="nav_style_selection")])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_context_input_keyboard():
        """Create context input/final confirmation keyboard"""
        keyboard = [
            [InlineKeyboardButton("✅ Start Monitoring", callback_data="action_start_monitoring")],
            [InlineKeyboardButton("📝 Add Custom Focus", callback_data="action_add_context")],
            [InlineKeyboardButton("⬅️ Back", callback_data="nav_interval_selection")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_context_editing_keyboard():
        """Create keyboard for custom context editing"""
        keyboard = [
            [InlineKeyboardButton("🚀 Start Monitoring", callback_data="action_start_monitoring")],
            [InlineKeyboardButton("✏️ Edit Focus", callback_data="action_add_context")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_already_active_keyboard():
        """Create keyboard when monitoring is already active"""
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_no_monitoring_keyboard():
        """Create keyboard when no monitoring is active"""
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="action_main_menu")]]
        return InlineKeyboardMarkup(keyboard)