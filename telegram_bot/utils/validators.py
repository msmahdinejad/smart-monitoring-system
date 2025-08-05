#!/usr/bin/env python3
"""
Validation Utilities for Telegram Bot
Handles input validation and data verification
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TelegramValidators:
    """Handle validation for Telegram bot inputs"""
    
    @staticmethod
    def validate_user_id(user_id: Any) -> bool:
        """Validate user ID format"""
        try:
            # Check if user_id can be converted to string and is not empty
            user_id_str = str(user_id)
            return user_id_str and user_id_str.strip() != ""
        except Exception:
            return False
    
    @staticmethod
    def validate_monitoring_type(monitoring_type: str) -> bool:
        """Validate monitoring type"""
        valid_types = ["security", "presence", "lighting", "classroom", "workplace", "custom"]
        return monitoring_type in valid_types
    
    @staticmethod
    def validate_prompt_style(prompt_style: str) -> bool:
        """Validate prompt style"""
        valid_styles = ["formal", "technical", "casual", "security", "report"]
        return prompt_style in valid_styles
    
    @staticmethod
    def validate_interval(interval: Any) -> bool:
        """Validate monitoring interval"""
        try:
            # Import config for validation bounds
            from config import MONITORING_CONFIG
            
            interval_int = int(interval)
            min_interval = MONITORING_CONFIG.get('min_interval', 5)
            max_interval = MONITORING_CONFIG.get('max_interval', 300)
            
            return min_interval <= interval_int <= max_interval
        except (ValueError, ImportError):
            return False
    
    @staticmethod
    def validate_custom_context(context: str) -> bool:
        """Validate custom context input"""
        try:
            # Check if context is string and within reasonable length
            if not isinstance(context, str):
                return False
            
            # Allow empty context (optional)
            if not context.strip():
                return True
            
            # Check length limits (1-500 characters)
            context_length = len(context.strip())
            return 1 <= context_length <= 500
        except Exception:
            return False
    
    @staticmethod
    def validate_session_config(session_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate complete session configuration"""
        try:
            # Check required fields
            required_fields = ["monitoring_type", "prompt_style", "interval"]
            for field in required_fields:
                if field not in session_data:
                    return False, f"Missing required field: {field}"
            
            # Validate monitoring type
            if not TelegramValidators.validate_monitoring_type(session_data["monitoring_type"]):
                return False, f"Invalid monitoring type: {session_data['monitoring_type']}"
            
            # Validate prompt style
            if not TelegramValidators.validate_prompt_style(session_data["prompt_style"]):
                return False, f"Invalid prompt style: {session_data['prompt_style']}"
            
            # Validate interval
            if not TelegramValidators.validate_interval(session_data["interval"]):
                return False, f"Invalid interval: {session_data['interval']}"
            
            # Validate custom context if present
            if "custom_context" in session_data:
                if not TelegramValidators.validate_custom_context(session_data["custom_context"]):
                    return False, "Invalid custom context format or length"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_callback_data(callback_data: str) -> bool:
        """Validate callback data format"""
        try:
            if not isinstance(callback_data, str) or not callback_data.strip():
                return False
            
            # Check callback data length (Telegram limit is 64 bytes)
            return len(callback_data.encode('utf-8')) <= 64
        except Exception:
            return False
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
        """Validate file size for Telegram upload"""
        try:
            max_size_bytes = max_size_mb * 1024 * 1024
            return 0 < file_size <= max_size_bytes
        except Exception:
            return False
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 500) -> str:
        """Sanitize text input for safe processing"""
        try:
            if not isinstance(text, str):
                return ""
            
            # Strip whitespace and limit length
            sanitized = text.strip()[:max_length]
            
            # Remove any potential control characters
            sanitized = ''.join(char for char in sanitized if char.isprintable() or char.isspace())
            
            return sanitized
        except Exception:
            return ""
    
    @staticmethod
    def validate_session_step(step: str) -> bool:
        """Validate session step"""
        valid_steps = [
            "type_selection", 
            "style_selection", 
            "interval_selection", 
            "context_input", 
            "awaiting_context"
        ]
        return step in valid_steps

class ConfigValidators:
    """Handle configuration validation"""
    
    @staticmethod
    def validate_telegram_config() -> tuple[bool, Optional[str]]:
        """Validate Telegram configuration"""
        try:
            from config import TELEGRAM_CONFIG
            
            # Check if enabled
            if not TELEGRAM_CONFIG.get('enabled', False):
                return False, "Telegram bot is disabled in configuration"
            
            # Check bot token
            bot_token = TELEGRAM_CONFIG.get('bot_token', '')
            if not bot_token or bot_token == "your_telegram_bot_token_here":
                return False, "Invalid or missing Telegram bot token"
            
            # Check chat_id
            chat_id = TELEGRAM_CONFIG.get('chat_id')
            if not chat_id:
                return False, "Missing chat_id in Telegram configuration"
            
            return True, None
            
        except ImportError:
            return False, "Failed to import Telegram configuration"
        except Exception as e:
            return False, f"Configuration validation error: {str(e)}"
    
    @staticmethod
    def validate_monitoring_config() -> tuple[bool, Optional[str]]:
        """Validate monitoring configuration"""
        try:
            from config import MONITORING_CONFIG
            
            # Check interval bounds
            min_interval = MONITORING_CONFIG.get('min_interval')
            max_interval = MONITORING_CONFIG.get('max_interval')
            default_interval = MONITORING_CONFIG.get('default_interval')
            
            if not all(isinstance(x, int) for x in [min_interval, max_interval, default_interval]):
                return False, "Monitoring intervals must be integers"
            
            if min_interval <= 0 or max_interval <= 0 or default_interval <= 0:
                return False, "Monitoring intervals must be positive"
            
            if min_interval >= max_interval:
                return False, "Min interval must be less than max interval"
            
            if not (min_interval <= default_interval <= max_interval):
                return False, "Default interval must be within min/max bounds"
            
            return True, None
            
        except ImportError:
            return False, "Failed to import monitoring configuration"
        except Exception as e:
            return False, f"Monitoring config validation error: {str(e)}"