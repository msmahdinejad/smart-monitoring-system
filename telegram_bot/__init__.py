#!/usr/bin/env python3
"""
Telegram Bot Package - Factory Functions and Initialization
Clean architecture implementation for Smart Environmental Monitoring System
"""

import logging
from .bot import TelegramMonitoringBot

logger = logging.getLogger(__name__)

def create_telegram_bot(main_app_instance):
    """Create and return enhanced Telegram bot instance with Video Only support"""
    try:
        from config import TELEGRAM_CONFIG
    except ImportError:
        logger.error("Failed to import TELEGRAM_CONFIG from config.py")
        return None
    
    if not TELEGRAM_CONFIG['enabled']:
        logger.info("Telegram bot is disabled in configuration")
        return None
    
    if not TELEGRAM_CONFIG['bot_token'] or TELEGRAM_CONFIG['bot_token'] == "your_telegram_bot_token_here":
        logger.error("Invalid Telegram bot token in configuration")
        return None
    
    try:
        bot = TelegramMonitoringBot(main_app_instance)
        logger.info("Enhanced Telegram bot with Video Only support created successfully")
        return bot
    except Exception as e:
        logger.error(f"Failed to create enhanced Telegram bot: {e}")
        return None

__all__ = ['create_telegram_bot', 'TelegramMonitoringBot']