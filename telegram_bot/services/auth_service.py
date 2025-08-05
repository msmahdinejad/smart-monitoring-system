#!/usr/bin/env python3
"""
Authorization Service for Telegram Bot
Handles user authentication and authorization
"""

import logging
from typing import Set

logger = logging.getLogger(__name__)

class AuthService:
    """Handle user authorization for Telegram bot"""
    
    def __init__(self, telegram_config: dict):
        """Initialize authorization service with Telegram configuration"""
        self.authorized_users: Set[str] = set()
        
        # Add chat_id as authorized user
        if telegram_config.get('chat_id'):
            self.authorized_users.add(str(telegram_config['chat_id']))
        
        # Add additional authorized users
        for user_id in telegram_config.get('authorized_users', []):
            self.authorized_users.add(str(user_id))
        
        logger.info(f"Initialized auth service with {len(self.authorized_users)} authorized users")
    
    def is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized to use the bot"""
        return str(user_id) in self.authorized_users
    
    def add_authorized_user(self, user_id: str) -> bool:
        """Add a new authorized user"""
        try:
            self.authorized_users.add(str(user_id))
            logger.info(f"Added authorized user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add authorized user {user_id}: {e}")
            return False
    
    def remove_authorized_user(self, user_id: str) -> bool:
        """Remove an authorized user"""
        try:
            self.authorized_users.discard(str(user_id))
            logger.info(f"Removed authorized user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove authorized user {user_id}: {e}")
            return False
    
    def get_authorized_users(self) -> Set[str]:
        """Get list of all authorized users"""
        return self.authorized_users.copy()
    
    def get_authorized_count(self) -> int:
        """Get count of authorized users"""
        return len(self.authorized_users)