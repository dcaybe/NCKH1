import os
import logging
import pickle
import hashlib
import shutil
from datetime import datetime
from typing import Optional, Dict, Any
from .config import CONFIG

logger = logging.getLogger(__name__)

def get_cache_key(prompt: str) -> str:
    """Generate cache key for LLM response."""
    return hashlib.md5(prompt.encode()).hexdigest()

def get_cached_response(prompt: str) -> Optional[str]:
    """Get cached LLM response if available."""
    try:
        llm_cache_path = os.path.join(CONFIG['cache_dir'], 'llm_cache.pkl')
        with open(llm_cache_path, 'rb') as f:
            cache = pickle.load(f)
        return cache.get(get_cache_key(prompt))
    except Exception:
        return None

def cache_response(prompt: str, response: str) -> None:
    """Cache LLM response for future use with LRU implementation."""
    try:
        llm_cache_path = os.path.join(CONFIG['cache_dir'], 'llm_cache.pkl')
        cache = {}
        
        # Load existing cache if available
        if os.path.exists(llm_cache_path):
            with open(llm_cache_path, 'rb') as f:
                cache = pickle.load(f)
        
        # Implement LRU-style cache
        if len(cache) >= CONFIG['llm_cache_size']:
            keys = list(cache.keys())
            for _ in range(len(cache) - CONFIG['llm_cache_size'] + 1):
                del cache[keys.pop(0)]
                
        cache[get_cache_key(prompt)] = response
        
        with open(llm_cache_path, 'wb') as f:
            pickle.dump(cache, f)
    except Exception as e:
        logger.error(f"Error caching response: {e}")

def setup_cache():
    """Initialize cache files and directories."""
    try:
        # Create cache directory if it doesn't exist
        if not os.path.exists(CONFIG['cache_dir']):
            os.makedirs(CONFIG['cache_dir'])
            logger.info("Created cache directory")

        # Create embedding cache file
        if not os.path.exists(CONFIG['embedding_cache_file']):
            with open(CONFIG['embedding_cache_file'], 'wb') as f:
                pickle.dump({}, f)
            logger.info("Created embedding cache file")
            
        # Create LLM cache file
        llm_cache = os.path.join(CONFIG['cache_dir'], 'llm_cache.pkl')
        if not os.path.exists(llm_cache):
            with open(llm_cache, 'wb') as f:
                pickle.dump({}, f)
            logger.info("Created LLM cache file")
            
        # Create conversation database
        if not os.path.exists(CONFIG['conversation_db']):
            import sqlite3
            conn = sqlite3.connect(CONFIG['conversation_db'])
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS conversations
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                assistant_message TEXT)
            ''')
            conn.commit()
            conn.close()
            logger.info("Created conversation database")
    except Exception as e:
        logger.error(f"Error initializing cache: {e}")
        raise

def backup_cache():
    """Create backups of important cache files."""
    try:
        backup_dir = os.path.join(CONFIG['cache_dir'], 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files_to_backup = [
            CONFIG['embedding_cache_file'],
            os.path.join(CONFIG['cache_dir'], 'llm_cache.pkl'),
            CONFIG['conversation_db']
        ]
        
        for file in files_to_backup:
            if os.path.exists(file):
                filename = os.path.basename(file)
                backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
                shutil.copy2(file, backup_path)
                
        logger.info("Created cache backup")
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        logger.warning("Continuing without backup")

def save_conversation(user_message: str, assistant_message: str):
    """Save conversation to SQLite database."""
    try:
        import sqlite3
        conn = sqlite3.connect(CONFIG['conversation_db'])
        c = conn.cursor()
        c.execute('''
            INSERT INTO conversations (timestamp, user_message, assistant_message)
            VALUES (?, ?, ?)
        ''', (datetime.now().isoformat(), user_message, assistant_message))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving conversation: {e}")

def get_conversation_history(limit: int = None) -> list:
    """Get conversation history from database."""
    try:
        import sqlite3
        conn = sqlite3.connect(CONFIG['conversation_db'])
        c = conn.cursor()
        
        if limit:
            c.execute('SELECT * FROM conversations ORDER BY id DESC LIMIT ?', (limit,))
        else:
            c.execute('SELECT * FROM conversations ORDER BY id DESC')
            
        rows = c.fetchall()
        conn.close()
        
        # Convert to list of dicts for easier handling
        history = []
        for row in rows:
            history.append({
                'id': row[0],
                'timestamp': row[1],
                'user_message': row[2],
                'assistant_message': row[3]
            })
        return history
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return []

def clear_cache():
    """Clear all cache files."""
    try:
        # Backup before clearing
        backup_cache()
        
        # Clear LLM cache
        llm_cache_path = os.path.join(CONFIG['cache_dir'], 'llm_cache.pkl')
        if os.path.exists(llm_cache_path):
            with open(llm_cache_path, 'wb') as f:
                pickle.dump({}, f)
                
        # Clear embedding cache
        if os.path.exists(CONFIG['embedding_cache_file']):
            with open(CONFIG['embedding_cache_file'], 'wb') as f:
                pickle.dump({}, f)
                
        # Clear FAISS index
        faiss_path = os.path.join(CONFIG['cache_dir'], 'faiss.index')
        if os.path.exists(faiss_path):
            os.remove(faiss_path)
            
        logger.info("Cleared all cache files")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")