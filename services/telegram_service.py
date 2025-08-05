"""
Telegram Service
Manages Telegram bot for notifications and commands
"""

import os
import logging
import requests

try:
    from config import TELEGRAM_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram Bot for sending monitoring notifications"""
    
    def __init__(self):
        self.enabled = TELEGRAM_CONFIG['enabled']
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.session = requests.Session()
        self.session.timeout = TELEGRAM_CONFIG['timeout']
        
        if self.enabled and self._validate_config():
            logger.info("Telegram Bot initialized successfully")
        elif self.enabled:
            logger.warning("Telegram Bot disabled due to configuration errors")
            self.enabled = False
    
    def _validate_config(self):
        """Validate Telegram configuration"""
        if not self.bot_token or self.bot_token == "your_telegram_bot_token_here":
            logger.error("❌ Invalid Telegram bot token")
            return False
        
        if not self.chat_id or self.chat_id == "your_chat_id_here":
            logger.error("❌ Invalid Telegram chat ID")
            return False
        
        return True
    
    def send_message(self, text, disable_notification=False):
        """Send text message to Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_notification': disable_notification
            }
            
            response = self.session.post(url, data=data)
            if response.status_code == 200:
                logger.debug("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Telegram message failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False
    
    def send_photo(self, image_path, caption="", disable_notification=False):
        """Send photo to Telegram"""
        if not self.enabled:
            return False
        
        try:
            file_size = os.path.getsize(image_path)
            if file_size > TELEGRAM_CONFIG['max_image_size']:
                logger.warning(f"Image too large for Telegram: {file_size} bytes")
                return False
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML',
                    'disable_notification': disable_notification
                }
                
                response = self.session.post(url, files=files, data=data)
                
            if response.status_code == 200:
                logger.debug("Telegram photo sent successfully")
                return True
            else:
                logger.error(f"Telegram photo failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram photo error: {e}")
            return False
    
    def send_video(self, video_path, caption="", disable_notification=False):
        """Send video to Telegram"""
        if not self.enabled:
            return False
        
        try:
            file_size = os.path.getsize(video_path)
            if file_size > 50 * 1024 * 1024:  # 50MB limit for videos
                logger.warning(f"Video too large for Telegram: {file_size} bytes")
                return False
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendVideo"
            
            with open(video_path, 'rb') as video:
                files = {'video': video}
                data = {
                    'chat_id': self.chat_id,
                    'caption': caption,
                    'parse_mode': 'HTML',
                    'disable_notification': disable_notification
                }
                
                response = self.session.post(url, files=files, data=data)
                
            if response.status_code == 200:
                logger.debug("Telegram video sent successfully")
                return True
            else:
                logger.error(f"Telegram video failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Telegram video error: {e}")
            return False
    
    def send_analysis_result(self, analysis_result, session_id, monitoring_type, 
                           baseline_path, current_path, timestamp, video_path=None):
        """Send complete analysis result with optional video to Telegram"""
        if not self.enabled:
            return False
        
        # Check if we should send based on status
        status = analysis_result.get('status', 'NORMAL')
        if status not in TELEGRAM_CONFIG['send_on_status']:
            logger.debug(f"Skipping Telegram notification for status: {status}")
            return False
        
        # Check if we should send based on threat level
        threat_level = analysis_result.get('threat_level', 0)
        if threat_level < TELEGRAM_CONFIG['send_on_threat_level']:
            logger.debug(f"Skipping Telegram notification for threat level: {threat_level}")
            return False
        
        try:
            # Format message
            message = self._format_analysis_message(analysis_result, session_id, monitoring_type, timestamp)
            
            # Send current image with analysis
            if TELEGRAM_CONFIG['send_images'] and os.path.exists(current_path):
                self.send_photo(current_path, message, disable_notification=(status == 'NORMAL'))
            
            # Send video if available and threat level is high
            if video_path and os.path.exists(video_path) and threat_level >= 5:
                video_caption = f"🎥 <b>Security Video</b>\n📊 Threat Level: {threat_level}/10\n🕒 Session: <code>{session_id}</code>"
                self.send_video(video_path, video_caption, disable_notification=False)
            
            logger.info(f"Telegram notification sent for {status} alert")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram analysis result: {e}")
            return False
    
    def _format_analysis_message(self, analysis_result, session_id, monitoring_type, timestamp):
        """Format analysis result for Telegram message"""
        status_emoji = {
            'NORMAL': '✅',
            'WARNING': '⚠️', 
            'DANGER': '🚨'
        }
        
        threat_level = analysis_result.get('threat_level', 0)
        if threat_level >= 8:
            threat_emoji = '🚨🚨'
        elif threat_level >= 5:
            threat_emoji = '⚠️'
        else:
            threat_emoji = '✅'
        
        status = analysis_result.get('status', 'UNKNOWN')
        confidence = analysis_result.get('confidence', 0)
        summary = analysis_result.get('summary', 'No summary available')
        
        if TELEGRAM_CONFIG['message_format'] == 'simple':
            message = f"""{status_emoji.get(status, '❓')} <b>Monitoring Alert</b>
            
<b>Status:</b> {status}
<b>Confidence:</b> {confidence:.1f}%
<b>Summary:</b> {summary}

<i>Time:</i> {timestamp}"""
        else:
            message = f"""🎥 <b>Smart Monitoring System</b>

{status_emoji.get(status, '❓')} <b>Status:</b> {status}
📊 <b>Confidence:</b> {confidence:.1f}%
{threat_emoji} <b>Threat Level:</b> {threat_level}/10

📋 <b>Type:</b> {monitoring_type.title()}
📄 <b>Summary:</b> {summary}

🔗 <b>Session:</b> <code>{session_id}</code>
🕒 <b>Time:</b> {timestamp}

---
💡 <i>Automated analysis with video recording</i>"""
        
        return message
    
    def test_connection(self):
        """Test Telegram bot connection"""
        if not self.enabled:
            return False, "Telegram bot is disabled"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data['ok']:
                    bot_name = data['result']['username']
                    return True, f"Connected to bot: @{bot_name}"
                else:
                    return False, "Invalid bot token"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)