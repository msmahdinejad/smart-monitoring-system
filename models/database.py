"""
Database Models and Manager
Handles all database operations for the monitoring system
"""

import os
import sqlite3
import logging
from datetime import datetime

try:
    from config import DATABASE_CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    exit(1)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for monitoring records"""
    
    def __init__(self):
        self.db_path = DATABASE_CONFIG['name']
    
    def init_database(self):
        """Initialize SQLite database with enhanced configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                baseline_path TEXT NOT NULL,
                current_path TEXT NOT NULL,
                video_path TEXT,
                monitoring_type TEXT NOT NULL,
                prompt_style TEXT NOT NULL,
                custom_context TEXT,
                prompt_used TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                threat_level INTEGER DEFAULT 0,
                summary TEXT,
                keywords TEXT,
                has_video BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON records(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON records(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON records(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_threat_level ON records(threat_level)')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def save_record(self, session_id, baseline_path, current_path, monitoring_type, 
                   prompt_style, custom_context, prompt_used, ai_response, analysis_result, video_path=None):
        """Save monitoring record with video support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        has_video = video_path is not None and os.path.exists(video_path)
        
        cursor.execute('''
            INSERT INTO records (
                timestamp, session_id, baseline_path, current_path, video_path, monitoring_type,
                prompt_style, custom_context, prompt_used, ai_response, status,
                confidence, threat_level, summary, keywords, has_video
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, session_id, baseline_path, current_path, video_path, monitoring_type,
            prompt_style, custom_context, prompt_used, ai_response, analysis_result['status'],
            analysis_result['confidence'], analysis_result['threat_level'], 
            analysis_result['summary'], analysis_result.get('action', ''), has_video
        ))
        
        conn.commit()
        conn.close()
        
        # Auto cleanup if enabled
        if DATABASE_CONFIG['auto_cleanup'] and DATABASE_CONFIG['max_records'] > 0:
            self.cleanup_old_records()
    
    def get_records(self, limit=50):
        """Get monitoring records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM records 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        records = cursor.fetchall()
        conn.close()
        return records
    
    def cleanup_old_records(self):
        """Clean up old records if max_records is exceeded"""
        if DATABASE_CONFIG['max_records'] <= 0:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count total records
        cursor.execute('SELECT COUNT(*) FROM records')
        total_records = cursor.fetchone()[0]
        
        if total_records > DATABASE_CONFIG['max_records']:
            # Delete oldest records
            records_to_delete = total_records - DATABASE_CONFIG['max_records']
            cursor.execute('''
                DELETE FROM records 
                WHERE id IN (
                    SELECT id FROM records 
                    ORDER BY timestamp ASC 
                    LIMIT ?
                )
            ''', (records_to_delete,))
            
            conn.commit()
            logger.info(f"Cleaned up {records_to_delete} old records")
        
        conn.close()