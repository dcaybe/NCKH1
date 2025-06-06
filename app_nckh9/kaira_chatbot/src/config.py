import os
import json
import logging
from typing import Dict, Any

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load hoặc tạo file config.json với cấu hình mặc định"""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # kaira_chatbot folder
    
    default_config = {
        "doc_folder": os.path.join(current_dir, "doc"),
        "model_folder": os.path.join(current_dir, "model"),
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "cache_dir": os.path.join(current_dir, "cache"),
        "top_k": 5,
        "chunk_size": 800,
        "min_text_length": 30,
        "max_workers": 8,
        "faiss_nlist": 10,
        "conversation_db": os.path.join(current_dir, "cache", "conversations.db"),
        "max_context_messages": 5,
        "llm_cache_size": 1000,
        "batch_size": 64,
        "embedding_cache_size": 10000,
        "embedding_cache_file": os.path.join(current_dir, "cache", "embedding_cache.pkl")
    }
    
    config_path = os.path.join(current_dir, 'config.json')
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
            logger.info("Đã tạo file config.json với cấu hình mặc định")
        return default_config
        
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load config mặc định
CONFIG = load_config()