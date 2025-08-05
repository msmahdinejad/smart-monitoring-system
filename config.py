#!/usr/bin/env python3
"""
Configuration File - Smart Environmental Monitoring System with Telegram Bot
Store all sensitive and critical variables here
"""

import os
from pathlib import Path

# ==================== ESP32-CAM Configuration ====================
ESP32_CAM_CONFIG = {
    "ip_address": "192.168.1.100",  # TODO: Replace with your ESP32-CAM IP address
    "timeout": 10,                  # Connection timeout in seconds
    "retry_count": 3,               # Number of retry attempts for capture
    "retry_delay": 2                # Delay between retries in seconds
}

# ==================== Enhanced Telegram Bot Configuration ====================
TELEGRAM_CONFIG = {
    # Basic Bot Settings
    "bot_token": "your_telegram_bot_token_here",      # TODO: Get from @BotFather on Telegram
    "chat_id": "your_chat_id_here",                   # TODO: Get your chat ID from @userinfobot
    "enabled": True,                                  # Enable/disable Telegram bot functionality
    
    # Notification Settings
    "send_images": True,                              # Send captured images in notifications
    "send_baseline": False,                           # Send baseline image (to reduce spam)
    "send_on_threat_level": 0,                        # Minimum threat level to send (0=all, 10=only critical)
    "send_on_status": ["NORMAL", "WARNING", "DANGER"], # Which statuses to send notifications for
    "message_format": "detailed",                     # "simple" or "detailed" message format
    
    # Technical Settings
    "max_image_size": 5 * 1024 * 1024,               # 5MB max image size for Telegram
    "timeout": 30,                                    # API timeout for Telegram requests
    "max_retries": 3,                                 # Max retries for failed messages
    "retry_delay": 2,                                 # Delay between retries
    
    # Bot Features
    "enable_capture": True,                           # Allow remote image capture via bot
    "enable_monitoring_control": True,                # Allow start/stop monitoring via bot
    "enable_history_access": True,                    # Allow viewing history via bot
    "enable_status_check": True,                      # Allow status checking via bot
    "enable_settings_view": True,                     # Allow settings viewing via bot
    
    # Security Settings
    "authorized_users": ["your_chat_id_here"],        # TODO: List of authorized chat IDs (as strings)
    "admin_chat_id": "your_chat_id_here",             # TODO: Admin chat ID for critical notifications
    "enable_user_verification": True,                 # Verify users before allowing access
    
    # Advanced Features
    "enable_inline_keyboards": True,                  # Use interactive inline keyboards
    "auto_delete_temp_images": True,                  # Auto-delete temporary images after sending
    "log_bot_interactions": True,                     # Log all bot interactions
    "enable_typing_indicator": True,                  # Show "typing..." indicator during processing
}

# ==================== AvalAI API Configuration ====================
AVALAI_CONFIG = {
    "api_key": "your_avalai_api_key_here",            # TODO: Get your AvalAI API key - KEEP SECRET!
    "base_url": "https://api.avalai.ir/v1",           # API base URL
    "model": "gpt-4o",                                # Default model to use
    "max_tokens": 400,                                # Maximum tokens per request
    "temperature": 0.1,                               # Temperature for consistent analysis
    "timeout": 45,                                    # API request timeout in seconds
    "max_retries": 3,                                 # Maximum retries for failed API calls
    "retry_delay": 5,                                 # Delay between API retries
    "enable_caching": False,                          # Cache API responses (saves costs)
    "cache_duration": 300,                            # Cache duration in seconds
}

# ==================== Database Configuration ====================
DATABASE_CONFIG = {
    "name": "monitoring.db",         # SQLite database filename
    "backup_enabled": True,          # Enable automatic backups
    "backup_interval": 24,           # Hours between backups
    "max_records": 10000,            # Maximum records to keep (0 = unlimited)
    "auto_cleanup": True,            # Enable automatic old record cleanup
    "cleanup_interval": 24,          # Hours between cleanup runs
    "backup_directory": "backups",   # Directory for database backups
}

# ==================== Server Configuration ====================
SERVER_CONFIG = {
    "host": "0.0.0.0",              # Server host (0.0.0.0 for all interfaces)
    "port": 5000,                   # Server port
    "debug": False,                 # Debug mode (set to False in production)
    "threaded": True,               # Enable threading
    "max_content_length": 16 * 1024 * 1024,  # 16MB max upload size
    "session_timeout": 3600,        # Session timeout in seconds
    "enable_cors": True,            # Enable CORS for API access
}

# ==================== Enhanced Monitoring Configuration ====================
MONITORING_CONFIG = {
    # Timing Settings
    "default_interval": 15,         # Default monitoring interval in seconds
    "min_interval": 5,              # Minimum allowed interval
    "max_interval": 3600,           # Maximum allowed interval (1 hour)
    
    # Image Settings
    "image_quality": 85,            # JPEG quality for saved images (1-100)
    "max_image_size": 2 * 1024 * 1024,  # 2MB max image size
    "image_format": "JPEG",         # Image format (JPEG/PNG)
    
    # Session Management
    "session_cleanup_interval": 300,     # Clean old sessions every 5 minutes
    "max_concurrent_sessions": 5,        # Maximum concurrent monitoring sessions
    "session_timeout": 7200,             # Session timeout in seconds (2 hours)
    
    # Performance Settings
    "max_capture_retries": 3,       # Maximum retries for image capture
    "capture_retry_delay": 2,       # Delay between capture retries
    "enable_image_compression": True, # Compress images to save space
    "compression_quality": 75,      # Compression quality (1-100)
    
    # Advanced Features
    "enable_motion_detection": False,  # Enable basic motion detection
    "motion_threshold": 30,           # Motion detection sensitivity (1-100)
    "enable_auto_baseline_update": False, # Auto-update baseline image
    "baseline_update_interval": 3600,     # Hours between baseline updates
}

# ==================== Storage Configuration ====================
STORAGE_CONFIG = {
    # Directories
    "images_directory": "static/images",    # Directory for storing images
    "logs_directory": "logs",              # Directory for log files
    "backups_directory": "backups",        # Directory for database backups
    "temp_directory": "temp",              # Directory for temporary files
    
    # Storage Limits
    "max_disk_usage": 1024 * 1024 * 1024, # 1GB max disk usage for images
    "max_image_age_days": 30,              # Delete images older than 30 days
    "max_log_size": 100 * 1024 * 1024,    # 100MB max log file size
    "max_backup_age_days": 90,             # Delete backups older than 90 days
    
    # Auto-cleanup Settings
    "auto_cleanup_enabled": True,          # Enable automatic cleanup
    "cleanup_schedule": "daily",           # Cleanup schedule (daily/weekly)
    "cleanup_time": "02:00",              # Time to run cleanup (HH:MM format)
    
    # File Management
    "enable_file_compression": True,       # Compress old files
    "compression_age_days": 7,             # Compress files older than 7 days
    "enable_file_encryption": False,       # Encrypt sensitive files
}

# ==================== Security Configuration ====================
SECURITY_CONFIG = {
    # File Security
    "allowed_file_types": [".jpg", ".jpeg", ".png"],  # Allowed image file types
    "max_filename_length": 255,                       # Maximum filename length
    "sanitize_filenames": True,                       # Sanitize uploaded filenames
    
    # Access Control
    "max_sessions_per_ip": 3,                         # Max sessions per IP address
    "rate_limit_requests": 100,                       # Max requests per hour per IP
    "enable_rate_limiting": True,                     # Enable rate limiting
    "blocked_ips": [],                                # List of blocked IP addresses
    
    # Web Security
    "enable_cors": True,                              # Enable CORS for API
    "cors_origins": ["*"],                            # Allowed CORS origins
    "secret_key": "change-this-secret-key-in-production",  # TODO: Change this Flask secret key!
    "session_cookie_secure": False,                   # Use secure cookies (enable in production)
    "session_cookie_httponly": True,                  # HTTP-only cookies
    
    # Admin Panel (Use with caution)
    "admin_password": "change-this-admin-password",   # TODO: Change this admin panel password!
    "enable_admin_panel": False,                      # Enable admin panel (security risk)
    "admin_session_timeout": 1800,                    # Admin session timeout (30 minutes)
    
    # API Security
    "require_api_key": False,                         # Require API key for web API
    "api_key": "",                                    # API key for web access
    "enable_api_logging": True,                       # Log API requests
    
    # Telegram Security
    "telegram_webhook_secret": "",                    # Webhook secret for Telegram
    "enable_telegram_rate_limit": True,               # Rate limit Telegram requests
    "max_telegram_requests_per_minute": 30,           # Max Telegram requests per minute
}

# ==================== Enhanced Logging Configuration ====================
LOGGING_CONFIG = {
    # Basic Settings
    "level": "INFO",                       # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
    # File Logging
    "file_enabled": True,                  # Enable logging to file
    "file_name": "monitoring.log",         # Log file name
    "max_file_size": 10 * 1024 * 1024,    # 10MB max log file size
    "backup_count": 5,                     # Number of backup log files
    "log_rotation": "size",                # Rotation method: "size" or "time"
    
    # Console Logging
    "console_enabled": True,               # Enable console logging
    "console_level": "INFO",               # Console logging level
    "colored_output": True,                # Enable colored console output
    
    # Advanced Logging
    "log_sql_queries": False,              # Log database queries
    "log_api_requests": True,              # Log API requests and responses
    "log_telegram_messages": True,         # Log Telegram bot interactions
    "log_image_operations": False,         # Log image capture and processing
    "sensitive_data_masking": True,        # Mask sensitive data in logs
    
    # Performance Logging
    "log_performance_metrics": True,       # Log performance metrics
    "performance_log_interval": 300,       # Performance logging interval (seconds)
    "log_memory_usage": True,              # Log memory usage
    "log_cpu_usage": True,                 # Log CPU usage
}

# ==================== AI Analysis Configuration ====================
AI_CONFIG = {
    # AI Service Settings
    "ai_enabled": True,                    # True = Use real AI, False = Test mode
    "test_mode": False,                    # Enable test mode functionality
    
    # Analysis Settings
    "confidence_threshold": 70,            # Minimum confidence for valid analysis
    "threat_level_threshold": 5,           # Threat level that triggers alerts
    "analysis_timeout": 60,                # Maximum time for analysis (seconds)
    
    # Test Mode Settings
    "test_mode_rotation": True,            # Rotate between different test responses
    "test_response_pattern": "random",     # "sequential", "random", "fixed"
    "fixed_test_response": "normal",       # Used when pattern is "fixed"
    
    # Test Mode Responses - Pre-defined responses for testing
    "test_responses": {
        "normal": {
            "status": "NORMAL",
            "confidence": 85.0,
            "threat_level": 1,
            "summary": "Test Mode: No significant changes detected in environment",
            "analysis": "Test Mode Response: Environment appears stable with normal lighting and no suspicious activity.",
            "action": "Continue monitoring - no action required"
        },
        "warning": {
            "status": "WARNING", 
            "confidence": 92.0,
            "threat_level": 6,
            "summary": "Test Mode: Minor environmental changes detected",
            "analysis": "Test Mode Response: Some objects may have moved or lighting conditions changed slightly.",
            "action": "Monitor closely for additional changes"
        },
        "danger": {
            "status": "DANGER",
            "confidence": 96.0, 
            "threat_level": 9,
            "summary": "Test Mode: Significant changes or potential security threat detected",
            "analysis": "Test Mode Response: Major environmental changes detected - possible intrusion or equipment failure.",
            "action": "Immediate attention required - verify environment manually"
        },
        "lighting": {
            "status": "WARNING",
            "confidence": 88.0,
            "threat_level": 3,
            "summary": "Test Mode: Lighting condition changes detected",
            "analysis": "Test Mode Response: Additional lights turned on or off - significant brightness level change detected.",
            "action": "Check electrical and lighting settings"
        },
        "movement": {
            "status": "WARNING",
            "confidence": 90.0,
            "threat_level": 4,
            "summary": "Test Mode: Signs of movement or activity detected",
            "analysis": "Test Mode Response: Objects may have moved or human presence detected in the environment.",
            "action": "Verify recent activity in the area"
        },
        "equipment": {
            "status": "WARNING",
            "confidence": 87.0,
            "threat_level": 5,
            "summary": "Test Mode: Equipment status change detected",
            "analysis": "Test Mode Response: Devices may have powered on/off or changed operational status.",
            "action": "Check equipment functionality and power status"
        }
    },
    
    # Real AI Settings (only when ai_enabled = True)
    "retry_failed_analysis": True,         # Retry failed AI analysis
    "max_analysis_retries": 2,             # Maximum retries for failed analysis
    "retry_delay": 5,                      # Delay between analysis retries
    
    # Caching
    "cache_responses": False,              # Cache AI responses (saves API calls)
    "cache_duration": 300,                 # Cache duration in seconds
    "cache_by_image_hash": True,           # Cache based on image hash
    
    # Prompt Engineering
    "enable_prompt_optimization": True,    # Enable automatic prompt optimization
    "custom_system_prompt": "",            # Custom system prompt (optional)
    "enable_context_learning": False,      # Learn from previous analyses
    
    # Response Processing
    "enable_response_validation": True,    # Validate AI responses
    "enable_confidence_scoring": True,     # Score response confidence
    "enable_threat_classification": True,  # Classify threats automatically
    
    # Monitoring Types and Styles (for reference)
    "supported_monitoring_types": [
        "security", "presence", "lighting", 
        "classroom", "workplace", "custom"
    ],
    "supported_prompt_styles": [
        "formal", "technical", "casual", 
        "security", "report"
    ],
}

# Helper functions for test mode
def get_test_response():
    """Get test response based on settings"""
    import random
    import time
    
    if not AI_CONFIG['test_mode']:
        return None
    
    responses = AI_CONFIG['test_responses']
    pattern = AI_CONFIG['test_response_pattern']
    
    if pattern == "fixed":
        response_key = AI_CONFIG['fixed_test_response']
        return responses.get(response_key, responses['normal'])
    
    elif pattern == "random":
        response_key = random.choice(list(responses.keys()))
        return responses[response_key]
    
    elif pattern == "sequential":
        # Use timestamp to cycle through responses
        response_keys = list(responses.keys())
        index = int(time.time() / 30) % len(response_keys)  # Change every 30 seconds
        return responses[response_keys[index]]
    
    # Default fallback
    return responses['normal']

def is_ai_enabled():
    """Check if real AI is enabled"""
    return AI_CONFIG.get('ai_enabled', False) and not AI_CONFIG.get('test_mode', True)

def get_test_mode_status():
    """Get test mode status information"""
    return {
        "test_mode": AI_CONFIG['test_mode'],
        "ai_enabled": AI_CONFIG['ai_enabled'],
        "pattern": AI_CONFIG['test_response_pattern'],
        "available_responses": list(AI_CONFIG['test_responses'].keys())
    }

# ==================== Notification Configuration ====================
NOTIFICATION_CONFIG = {
    # Email Notifications (optional - not implemented in base version)
    "email_enabled": False,
    "smtp_server": "",
    "smtp_port": 587,
    "email_username": "",
    "email_password": "",
    "recipient_emails": [],
    
    # Webhook Notifications (optional)
    "webhook_enabled": False,
    "webhook_url": "",
    "webhook_secret": "",
    "webhook_timeout": 10,
    
    # Alert Escalation
    "enable_escalation": False,            # Enable alert escalation
    "escalation_threshold": 8,             # Threat level for escalation
    "escalation_delay": 300,               # Delay before escalation (seconds)
    "escalation_contacts": [],             # Escalation contact list
}

# ==================== Environment Variables Override ====================
# Allow overriding configuration with environment variables for deployment

def load_env_config():
    """Load configuration from environment variables if available"""
    
    # ESP32-CAM Configuration
    if os.getenv('ESP32_CAM_IP'):
        ESP32_CAM_CONFIG['ip_address'] = os.getenv('ESP32_CAM_IP')
    
    # AvalAI Configuration
    if os.getenv('AVALAI_API_KEY'):
        AVALAI_CONFIG['api_key'] = os.getenv('AVALAI_API_KEY')
    
    if os.getenv('AVALAI_BASE_URL'):
        AVALAI_CONFIG['base_url'] = os.getenv('AVALAI_BASE_URL')
    
    if os.getenv('AVALAI_MODEL'):
        AVALAI_CONFIG['model'] = os.getenv('AVALAI_MODEL')
    
    # Server Configuration
    if os.getenv('SERVER_HOST'):
        SERVER_CONFIG['host'] = os.getenv('SERVER_HOST')
    
    if os.getenv('SERVER_PORT'):
        SERVER_CONFIG['port'] = int(os.getenv('SERVER_PORT'))
    
    if os.getenv('DEBUG'):
        SERVER_CONFIG['debug'] = os.getenv('DEBUG').lower() == 'true'
    
    # Security Configuration
    if os.getenv('SECRET_KEY'):
        SECURITY_CONFIG['secret_key'] = os.getenv('SECRET_KEY')
    
    if os.getenv('ADMIN_PASSWORD'):
        SECURITY_CONFIG['admin_password'] = os.getenv('ADMIN_PASSWORD')
    
    # Telegram Configuration
    if os.getenv('TELEGRAM_BOT_TOKEN'):
        TELEGRAM_CONFIG['bot_token'] = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if os.getenv('TELEGRAM_CHAT_ID'):
        TELEGRAM_CONFIG['chat_id'] = os.getenv('TELEGRAM_CHAT_ID')
    
    if os.getenv('TELEGRAM_ENABLED'):
        TELEGRAM_CONFIG['enabled'] = os.getenv('TELEGRAM_ENABLED').lower() == 'true'

# ==================== Configuration Validation ====================
def validate_config():
    """Validate critical configuration values"""
    errors = []
    
    # Check AvalAI API key
    if AVALAI_CONFIG['api_key'] == "your_avalai_api_key_here" or not AVALAI_CONFIG['api_key']:
        errors.append("❌ AVALAI_API_KEY is not set! Please update config.py or set environment variable.")
    
    # Check secret key
    if SECURITY_CONFIG['secret_key'] == "change-this-secret-key-in-production":
        errors.append("⚠️ WARNING: Default secret key detected. Please change it for security!")
    
    # Check admin password
    if SECURITY_CONFIG['admin_password'] == "change-this-admin-password":
        errors.append("⚠️ WARNING: Default admin password detected. Please change it!")
    
    # Check ESP32-CAM IP
    if not ESP32_CAM_CONFIG['ip_address'] or ESP32_CAM_CONFIG['ip_address'] == "192.168.1.100":
        errors.append("⚠️ WARNING: Please verify ESP32-CAM IP address is correct.")
    
    # Check Telegram configuration
    if TELEGRAM_CONFIG['enabled']:
        if TELEGRAM_CONFIG['bot_token'] == "your_telegram_bot_token_here" or not TELEGRAM_CONFIG['bot_token']:
            errors.append("❌ TELEGRAM_BOT_TOKEN is not set! Please update config.py or disable Telegram.")
        
        if TELEGRAM_CONFIG['chat_id'] == "your_chat_id_here" or not TELEGRAM_CONFIG['chat_id']:
            errors.append("❌ TELEGRAM_CHAT_ID is not set! Please update config.py or disable Telegram.")
        
        # Validate bot token format
        if TELEGRAM_CONFIG['bot_token'] and ":" not in TELEGRAM_CONFIG['bot_token']:
            errors.append("❌ Invalid Telegram bot token format! Should contain ':'")
        
        # Validate chat ID format
        if TELEGRAM_CONFIG['chat_id'] and not TELEGRAM_CONFIG['chat_id'].lstrip('-').isdigit():
            errors.append("❌ Invalid Telegram chat ID format! Should be numeric.")
    
    # Check directories exist and create them
    directories = [
        STORAGE_CONFIG['images_directory'],
        STORAGE_CONFIG['logs_directory'],
        STORAGE_CONFIG['backups_directory'],
        STORAGE_CONFIG.get('temp_directory', 'temp')
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"❌ Cannot create directory {directory}: {e}")
    
    # Validate monitoring intervals
    if MONITORING_CONFIG['min_interval'] < 1:
        errors.append("❌ Minimum monitoring interval must be at least 1 second.")
    
    if MONITORING_CONFIG['max_interval'] < MONITORING_CONFIG['min_interval']:
        errors.append("❌ Maximum monitoring interval must be greater than minimum.")
    
    # Validate image settings
    if not (1 <= MONITORING_CONFIG['image_quality'] <= 100):
        errors.append("❌ Image quality must be between 1 and 100.")
    
    # Validate AI settings
    if not (0 <= AI_CONFIG['confidence_threshold'] <= 100):
        errors.append("❌ Confidence threshold must be between 0 and 100.")
    
    if not (0 <= AI_CONFIG['threat_level_threshold'] <= 10):
        errors.append("❌ Threat level threshold must be between 0 and 10.")
    
    return errors

# ==================== Configuration Display ====================
def display_config():
    """Display current configuration (without sensitive data)"""
    print("📋 Smart Monitoring System Configuration:")
    print(f"   ESP32-CAM IP: {ESP32_CAM_CONFIG['ip_address']}")
    print(f"   Web Server: {SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
    print(f"   Database: {DATABASE_CONFIG['name']}")
    print(f"   Images Directory: {STORAGE_CONFIG['images_directory']}")
    print(f"   AI Model: {AVALAI_CONFIG['model']}")
    print(f"   Debug Mode: {SERVER_CONFIG['debug']}")
    print(f"   Logging Level: {LOGGING_CONFIG['level']}")
    
    # Telegram Bot Status
    if TELEGRAM_CONFIG['enabled']:
        print("   Telegram Bot: ✅ Enabled")
        enabled_features = sum([
            TELEGRAM_CONFIG['enable_capture'],
            TELEGRAM_CONFIG['enable_monitoring_control'], 
            TELEGRAM_CONFIG['enable_history_access'],
            TELEGRAM_CONFIG['enable_status_check'],
            TELEGRAM_CONFIG['enable_settings_view']
        ])
        print(f"   Bot Features: {enabled_features} of 5 features enabled")
        token_status = "✅ Set" if TELEGRAM_CONFIG['bot_token'] != 'your_telegram_bot_token_here' else "❌ Not Set"
        chat_status = "✅ Set" if TELEGRAM_CONFIG['chat_id'] != 'your_chat_id_here' else "❌ Not Set"
        print(f"   Bot Token: {token_status}")
        print(f"   Chat ID: {chat_status}")
        print(f"   Authorized Users: {len(TELEGRAM_CONFIG['authorized_users'])}")
    else:
        print("   Telegram Bot: ❌ Disabled")
    
    # Security Status
    security_score = 0
    if SECURITY_CONFIG['secret_key'] != "change-this-secret-key-in-production":
        security_score += 1
    if SECURITY_CONFIG['admin_password'] != "change-this-admin-password":
        security_score += 1
    if SECURITY_CONFIG['enable_rate_limiting']:
        security_score += 1
    if AVALAI_CONFIG['api_key'] != "your_avalai_api_key_here":
        security_score += 1
    
    print(f"   Security Score: {security_score}/4 {'✅' if security_score >= 3 else '⚠️'}")

# ==================== Helper Functions ====================
def get_telegram_bot_info():
    """Get Telegram bot information for display"""
    if not TELEGRAM_CONFIG['enabled']:
        return None
    
    return {
        "enabled": TELEGRAM_CONFIG['enabled'],
        "features_enabled": {
            "capture": TELEGRAM_CONFIG['enable_capture'],
            "monitoring": TELEGRAM_CONFIG['enable_monitoring_control'],
            "history": TELEGRAM_CONFIG['enable_history_access'],
            "status": TELEGRAM_CONFIG['enable_status_check'],
            "settings": TELEGRAM_CONFIG['enable_settings_view'],
        },
        "security": {
            "authorized_users": len(TELEGRAM_CONFIG['authorized_users']),
            "user_verification": TELEGRAM_CONFIG['enable_user_verification'],
        },
        "notifications": {
            "send_images": TELEGRAM_CONFIG['send_images'],
            "message_format": TELEGRAM_CONFIG['message_format'],
            "threat_threshold": TELEGRAM_CONFIG['send_on_threat_level'],
        }
    }

def get_system_status():
    """Get overall system status"""
    errors = validate_config()
    
    return {
        "config_valid": len(errors) == 0,
        "config_errors": errors,
        "telegram_enabled": TELEGRAM_CONFIG['enabled'],
        "ai_configured": AVALAI_CONFIG['api_key'] != "your_avalai_api_key_here",
        "camera_configured": ESP32_CAM_CONFIG['ip_address'] != "192.168.1.100",
        "security_level": "high" if len(errors) == 0 else "medium" if len(errors) < 3 else "low"
    }

# ==================== Auto-load environment variables ====================
load_env_config()

# ==================== Export commonly used values ====================
# For backward compatibility and easy access
ESP32_CAM_IP = ESP32_CAM_CONFIG['ip_address']
AVALAI_API_KEY = AVALAI_CONFIG['api_key']
AVALAI_BASE_URL = AVALAI_CONFIG['base_url']
DATABASE_NAME = DATABASE_CONFIG['name']
IMAGES_DIR = STORAGE_CONFIG['images_directory']
TELEGRAM_BOT_TOKEN = TELEGRAM_CONFIG['bot_token']
TELEGRAM_CHAT_ID = TELEGRAM_CONFIG['chat_id']

# ==================== Development vs Production Detection ====================
IS_DEVELOPMENT = SERVER_CONFIG['debug'] or os.getenv('ENVIRONMENT') == 'development'
IS_PRODUCTION = not IS_DEVELOPMENT

# ==================== Production Security Warning ====================
if IS_PRODUCTION:
    production_issues = []
    
    if SERVER_CONFIG['debug']:
        production_issues.append("Debug mode is enabled")
    
    if SECURITY_CONFIG['secret_key'] == "change-this-secret-key-in-production":
        production_issues.append("Default secret key is being used")
    
    if SECURITY_CONFIG['admin_password'] == "change-this-admin-password":
        production_issues.append("Default admin password is being used")
    
    if not SECURITY_CONFIG['session_cookie_secure']:
        production_issues.append("Secure cookies are disabled")
    
    if production_issues:
        print("🚨 PRODUCTION SECURITY WARNING:")
        for issue in production_issues:
            print(f"   ⚠️ {issue}")
        print("   Please review security settings before deployment!")

if __name__ == "__main__":
    # Configuration test/validation when run directly
    print("🔧 Smart Monitoring System - Enhanced Configuration Validator")
    print("=" * 70)
    
    load_env_config()
    errors = validate_config()
    
    if errors:
        print("❌ Configuration Issues Found:")
        for error in errors:
            print(f"   {error}")
        print()
    else:
        print("✅ Configuration validation passed!")
        print()
    
    display_config()
    
    # Show Telegram bot info
    bot_info = get_telegram_bot_info()
    if bot_info:
        print(f"\n🤖 Telegram Bot Status:")
        print(f"   Features: {sum(bot_info['features_enabled'].values())}/5 enabled")
        print(f"   Security: {bot_info['security']['authorized_users']} authorized users")
        print(f"   Notifications: {bot_info['notifications']['message_format']} format")
    
    # Show system status
    system_status = get_system_status()
    print(f"\n📊 System Status:")
    print(f"   Overall: {'✅ Ready' if system_status['config_valid'] else '⚠️ Needs attention'}")
    print(f"   Security Level: {system_status['security_level'].upper()}")
    
    print("=" * 70)
    
    if IS_DEVELOPMENT:
        print("🚀 Running in DEVELOPMENT mode")
    else:
        print("🏭 Running in PRODUCTION mode")
        if not system_status['config_valid']:
            print("⚠️ Please fix configuration issues before production deployment!")
