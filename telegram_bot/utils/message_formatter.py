#!/usr/bin/env python3
"""
Message Formatter Utilities for Telegram Bot
Handles message formatting and templating
"""

from datetime import datetime
from typing import Dict, Any, Optional, List

class MessageFormatter:
    """Handle message formatting for Telegram bot"""
    
    @staticmethod
    def format_welcome_message() -> str:
        """Format welcome message for /start command"""
        return """🎥 *Smart IoT Monitoring System*

Welcome to your ESP32-CAM monitoring assistant!

🔹 *Capture* instant images from ESP32-CAM
🔹 *Monitor* environment with AI analysis  
🔹 *Record* videos during monitoring
🔹 *View* monitoring history with video playback
🔹 *Control* all functions remotely

Use the menu below or type /help for commands."""
    
    @staticmethod
    def format_help_message() -> str:
        """Format help message"""
        return """📖 *Available Commands:*

🔹 `/start` - Show main menu
🔹 `/capture` - Take instant photo from ESP32-CAM
🔹 `/status` - View system status and info
🔹 `/history` - Show recent monitoring records
🔹 `/monitor_start` - Start AI monitoring
🔹 `/monitor_stop` - Stop current monitoring session
🔹 `/settings` - View system configuration
🔹 `/video_test` - Test video recording functionality
🔹 `/help` - Show this help message

*Quick Actions:*
• Use inline buttons for faster navigation
• All monitoring features available remotely
• Real-time notifications with video evidence

*System Features:*
✅ AI-powered image analysis
✅ Video recording and processing
✅ Multiple monitoring types
✅ Customizable alert styles
✅ Complete history tracking with media
✅ Remote control via Telegram"""
    
    @staticmethod
    def format_capture_result(timestamp: str, file_size: int, camera_ip: str) -> str:
        """Format capture result message"""
        return f"""📸 *Live Capture*
            
🕒 *Time:* {timestamp}
📏 *Size:* {file_size} bytes
📍 *Camera:* ESP32-CAM ({camera_ip})

*Image captured successfully from your monitoring system.*"""
    
    @staticmethod
    def format_system_status(status_data: Dict[str, Any]) -> str:
        """Format system status message"""
        return f"""📊 *System Status Report*

🎥 *Monitoring:* {status_data['monitoring_status']}
📷 *Camera:* {status_data['camera_status']}
🎬 *Video Recording:* {status_data['video_status']}
🆔 *Session ID:* `{status_data['session_id']}`
📁 *Total Records:* {status_data['total_records']}
🎞️ *Records with Video:* {status_data['video_records']}

🔧 *Configuration:*
• *Camera IP:* `{status_data['camera_ip']}`
• *Images Directory:* `{status_data['images_dir']}`
• *Videos Directory:* `{status_data['videos_dir']}`
• *Database:* `{status_data['database']}`
• *AI Model:* `{status_data['ai_model']}`

⏰ *Timestamp:* {status_data['timestamp']}"""
    
    @staticmethod
    def format_monitoring_history(records: List) -> str:
        """Format monitoring history"""
        if not records:
            return "📋 *No Records Found*\n\nStart monitoring to see analysis results here."
        
        history_text = "📋 *Recent Monitoring History*\n\n"
        
        for i, record in enumerate(records[:5], 1):
            record_id = record[0]
            timestamp = record[1]
            session_id = record[2]
            monitoring_type = record[6] if len(record) > 6 else "unknown"
            status = record[11] if len(record) > 11 else "UNKNOWN"
            confidence = record[12] if len(record) > 12 else 0
            threat_level = record[13] if len(record) > 13 else 0
            summary = record[14] if len(record) > 14 else "No summary"
            has_video = record[16] if len(record) > 16 else False
            
            status_emoji = {"NORMAL": "✅", "WARNING": "⚠️", "DANGER": "🚨"}.get(status, "❓")
            video_indicator = "🎥" if has_video else "📷"
            
            history_text += f"""*{i}. Record #{record_id}* {video_indicator}
{status_emoji} *Status:* {status} ({confidence:.1f}%)
🎯 *Threat Level:* {threat_level}/10
📋 *Type:* {monitoring_type}
📄 *Summary:* {summary[:50]}{'...' if len(summary) > 50 else ''}
🕒 *Time:* {timestamp}

"""
        
        return history_text
    
    @staticmethod
    def format_settings_message(config_data: Dict[str, Any]) -> str:
        """Format system settings"""
        return f"""⚙️ *System Configuration*

🎥 *ESP32-CAM Settings:*
• *IP Address:* `{config_data['camera_ip']}`
• *Timeout:* {config_data['camera_timeout']} seconds
• *Retry Count:* {config_data['camera_retry']}`

🤖 *AI Configuration:*
• *Model:* `{config_data['ai_model']}`
• *Max Tokens:* {config_data['ai_max_tokens']}
• *Temperature:* {config_data['ai_temperature']}

📊 *Monitoring Settings:*
• *Default Interval:* {config_data['default_interval']} seconds
• *Min Interval:* {config_data['min_interval']} seconds
• *Max Interval:* {config_data['max_interval']} seconds

💾 *Storage:*
• *Images Directory:* `{config_data['images_dir']}`
• *Videos Directory:* `{config_data['videos_dir']}`
• *Database:* `{config_data['database']}`

📱 *Telegram:*
• *Notifications:* {config_data['notifications_status']}
• *Send Images:* {config_data['send_images_status']}
• *Send Videos:* {config_data['send_videos_status']}`"""
    
    @staticmethod
    def format_monitoring_type_selection() -> str:
        """Format monitoring type selection message"""
        return """🎭 *Choose Your AI Professional*

🔒 **Security Guard** - Professional security monitoring
👥 **Facility Supervisor** - Building management monitoring
💡 **Electrical Technician** - Electrical systems monitoring
🎓 **Teacher** - Classroom monitoring
🏢 **Safety Officer** - Workplace safety monitoring
⚙️ **Custom Professional** - Define your own monitoring type

*The AI will adopt the chosen professional role and perspective.*"""
    
    @staticmethod
    def format_prompt_style_selection(role_desc: str) -> str:
        """Format prompt style selection message"""
        return f"""📝 *Choose Communication Style*

*Selected AI Role:* {role_desc}

📋 **Official Report** - Formal language for management
🔧 **Expert Technical** - Detailed technical specifications  
💬 **Friendly Colleague** - Easy everyday language
🚨 **Security Professional** - Alert-focused protective language
📊 **Executive Briefing** - Structured for decision makers

*Choose how your AI professional should communicate:*"""
    
    @staticmethod
    def format_interval_selection(type_name: str, style_name: str) -> str:
        """Format interval selection message"""
        return f"""⏰ *Select Monitoring Interval*

*Type:* {type_name}
*Style:* {style_name}

Choose how often to capture images and analyze:

⚡ **Fast (5-15s)** - Quick detection
⏱️ **Medium (30s-1m)** - Balanced monitoring  
🕐 **Slow (2m-5m)** - Extended observation

*Recommendation:* Use faster intervals for security/activity monitoring, slower for static environments."""
    
    @staticmethod
    def format_context_input(type_name: str, style_name: str, interval: int, monitoring_desc: str) -> str:
        """Format context input message"""
        return f"""🚀 *Ready to Start Monitoring*

*Configuration Summary:*
🎯 *Type:* {type_name}
📝 *Style:* {style_name}  
⏰ *Interval:* {interval} seconds

{monitoring_desc}

*Optional:* You can add specific focus areas or additional requirements to make the monitoring even more precise.

*Examples of custom focus:*
• "Pay special attention to the front door"
• "Monitor the specific red machine in corner"
• "Focus on detecting hand movements"
• "Watch for packages or deliveries"
• "Monitor pet activity and behavior"
• "Check for equipment malfunction signs"

Ready to start, or want to add custom focus?"""
    
    @staticmethod
    def format_monitoring_started(config: Dict[str, Any]) -> str:
        """Format monitoring started success message"""
        return f"""✅ *Monitoring Started Successfully*

🎯 *Type:* {config['type_name']}
📝 *Style:* {config['style_name']}
⏰ *Interval:* {config['interval']} seconds
{f"📄 *Focus:* {config['custom_context']}" if config.get('custom_context') else ""}

{config['monitoring_desc']}

🕒 *Started:* {config['timestamp']}

The AI will now analyze images every {config['interval']} seconds. You'll receive detailed analysis when significant changes are detected."""
    
    @staticmethod
    def format_monitoring_stopped(session_id: str) -> str:
        """Format monitoring stopped message"""
        return f"""⏹️ *Monitoring Stopped*

*Session ID:* `{session_id}`
*Stopped at:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The monitoring session has been terminated successfully."""
    
    @staticmethod
    def format_video_test_result(file_size: int, camera_ip: str) -> str:
        """Format video test result message"""
        return f"""🎥 *Video Test Results*

✅ *Status:* Recording successful
⏱️ *Duration:* 10 seconds
📏 *File Size:* {file_size:,} bytes
📍 *Camera:* ESP32-CAM ({camera_ip})

*Test video recorded successfully!*"""
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Format error message"""
        return f"❌ *Error*\n\n`{error}`"
    
    @staticmethod
    def format_access_denied() -> str:
        """Format access denied message"""
        return """❌ *Access Denied*

You are not authorized to use this bot.
Please contact the system administrator."""