#!/usr/bin/env python3
"""
Monitoring Service for Telegram Bot
Handles monitoring operations and status
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MonitoringService:
    """Handle monitoring operations for Telegram bot"""
    
    def __init__(self, main_app_instance):
        """Initialize monitoring service with main app reference"""
        self.main_app = main_app_instance
        
        # Monitoring types and descriptions
        self.monitoring_types = {
            "security": "🔒 Security Guard\n   👮‍♂️ Professional security monitoring\n   🚨 Detects intrusion, theft, unauthorized access\n   🎥 Records security footage",
            "presence": "👥 Facility Supervisor\n   🏢 Monitors human presence like building manager\n   📊 Tracks movement, attendance, utilization\n   🎬 Records activity patterns", 
            "lighting": "💡 Electrical Technician\n   ⚡ Professional electrical systems monitoring\n   🔧 Detects power changes, lighting status\n   📹 Documents equipment status",
            "classroom": "🎓 Teacher & Supervisor\n   👨‍🏫 Classroom monitoring with educator perspective\n   📚 Assesses engagement, learning environment\n   🎥 Records educational activities",
            "workplace": "🏢 Safety Officer\n   🦺 Workplace safety like certified inspector\n   📈 Monitors safety standards, productivity\n   📽️ Documents safety compliance",
            "custom": "⚙️ Custom Professional\n   🎯 AI adapts to any specific role you define\n   💼 Becomes exact expert monitor you need\n   🎦 Records custom scenarios"
        }

        self.prompt_styles = {
            "formal": "📋 Official Report\n   🏛️ Professional language for management\n   📊 Formal documentation style", 
            "technical": "🔧 Expert Technical\n   ⚙️ Detailed specifications and measurements\n   🔬 Professional technical language", 
            "casual": "💬 Friendly Colleague\n   😊 Easy everyday language\n   🤝 Approachable explanations", 
            "security": "🚨 Security Professional\n   👮‍♂️ Alert-focused like security personnel\n   🛡️ Protective threat assessment language",
            "report": "📊 Executive Briefing\n   💼 Structured for decision makers\n   📈 Professional consultant-style summary"
        }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status with thread safety"""
        try:
            return self.main_app.get_monitoring_state()
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {'active': False, 'session_id': None, 'baseline_path': None}
    
    def start_monitoring(self, interval: int, monitoring_type: str, prompt_style: str, custom_context: str) -> bool:
        """Start monitoring session with given parameters"""
        try:
            # Check if monitoring is already active
            status = self.get_monitoring_status()
            if status['active']:
                logger.warning("Monitoring is already active")
                return False
            
            # Start monitoring using new architecture
            success = self.main_app.monitoring_loop(interval, monitoring_type, prompt_style, custom_context)
            
            if success:
                logger.info(f"Started monitoring: type={monitoring_type}, style={prompt_style}, interval={interval}s")
            else:
                logger.error("Failed to start monitoring session")
            
            return success
            
        except Exception as e:
            logger.error(f"Error starting monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop current monitoring session"""
        try:
            # Check monitoring status
            status = self.get_monitoring_status()
            if not status['active']:
                logger.warning("No active monitoring session to stop")
                return False
            
            # Stop monitoring using new architecture
            self.main_app.monitoring_service.stop_monitoring()
            logger.info("Monitoring session stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring: {e}")
            return False
    
    def get_monitoring_history(self, limit: int = 10) -> List:
        """Get monitoring history records"""
        try:
            records = self.main_app.db_manager.get_records(limit)
            return records
        except Exception as e:
            logger.error(f"Error getting monitoring history: {e}")
            return []
    
    def get_monitoring_types(self) -> Dict[str, str]:
        """Get available monitoring types"""
        return self.monitoring_types.copy()
    
    def get_prompt_styles(self) -> Dict[str, str]:
        """Get available prompt styles"""
        return self.prompt_styles.copy()
    
    def validate_monitoring_config(self, monitoring_type: str, prompt_style: str, interval: int) -> bool:
        """Validate monitoring configuration parameters"""
        try:
            # Import config for validation
            from config import MONITORING_CONFIG
            
            # Check monitoring type
            if monitoring_type not in self.monitoring_types:
                logger.error(f"Invalid monitoring type: {monitoring_type}")
                return False
            
            # Check prompt style
            if prompt_style not in self.prompt_styles:
                logger.error(f"Invalid prompt style: {prompt_style}")
                return False
            
            # Check interval bounds
            min_interval = MONITORING_CONFIG.get('min_interval', 5)
            max_interval = MONITORING_CONFIG.get('max_interval', 300)
            
            if not (min_interval <= interval <= max_interval):
                logger.error(f"Invalid interval {interval}s. Must be between {min_interval}-{max_interval}s")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating monitoring config: {e}")
            return False