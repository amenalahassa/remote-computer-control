"""
Database module for storing chat history
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ChatDatabase:
    """Manages chat history in SQLite database"""
    
    def __init__(self, db_path: str = "src/chat_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if needed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT,
                        username TEXT,
                        role TEXT,
                        content TEXT,
                        message_type TEXT,
                        metadata TEXT
                    )
                """)
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                    ON messages(timestamp DESC)
                """)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def add_message(self, user_id: str, username: str, role: str, 
                   content: str, message_type: str = "text", 
                   metadata: Optional[Dict] = None):
        """Add a message to the history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute("""
                    INSERT INTO messages 
                    (user_id, username, role, content, message_type, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, username, role, content, message_type, metadata_json))
                
                conn.commit()
                logger.debug(f"Added message from {username} ({role})")
                
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
    
    def get_recent_messages(self, limit: int = 20) -> List[Dict]:
        """Get recent messages for context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT timestamp, user_id, username, role, content, 
                           message_type, metadata
                    FROM messages
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                
                messages = []
                for row in reversed(rows):  # Reverse to get chronological order
                    msg = {
                        'timestamp': row[0],
                        'user_id': row[1],
                        'username': row[2],
                        'role': row[3],
                        'content': row[4],
                        'message_type': row[5],
                        'metadata': json.loads(row[6]) if row[6] else None
                    }
                    messages.append(msg)
                
                logger.info(f"Retrieved {len(messages)} messages from history")
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def get_conversation_context(self, limit: int = 10) -> List[Dict]:
        """Get conversation context for Open Interpreter"""
        messages = self.get_recent_messages(limit)
        
        # Format for Open Interpreter
        context = []
        for msg in messages:
            if msg['role'] == 'user':
                context.append({
                    'role': 'user',
                    'type': 'message',
                    'content': msg['content']
                })
            elif msg['role'] == 'assistant':
                # Parse assistant messages based on type
                if msg['message_type'] == 'code':
                    context.append({
                        'role': 'assistant',
                        'type': 'code',
                        'format': msg['metadata'].get('language', 'python') if msg['metadata'] else 'python',
                        'content': msg['content']
                    })
                else:
                    context.append({
                        'role': 'assistant',
                        'type': 'message',
                        'content': msg['content']
                    })
        
        return context
    
    def clear_old_messages(self, days: int = 30):
        """Clear messages older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM messages
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
                
                deleted = cursor.rowcount
                conn.commit()
                
                logger.info(f"Deleted {deleted} messages older than {days} days")
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to clear old messages: {e}")
            return 0
    
    def export_history(self, output_path: str = "src/output/chat_history.json"):
        """Export chat history to JSON file"""
        try:
            messages = self.get_recent_messages(limit=1000)  # Get last 1000 messages
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(messages)} messages to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            return None