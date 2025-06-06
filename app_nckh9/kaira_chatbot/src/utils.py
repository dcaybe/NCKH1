import os
import logging
import nltk
from typing import Dict, Any
from dotenv import load_dotenv
from .config import CONFIG

def setup_nltk():
    """Download required NLTK resources."""
    try:
        print("Downloading NLTK resources...")
        nltk.download('punkt', quiet=True)
        print("Downloaded NLTK resources successfully")
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")
        raise

def setup_env():
    """Create .env template if it doesn't exist."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(current_dir, '.env')
    
    if not os.path.exists(env_path):
        env_content = """# API Keys
GOOGLE_API_KEY=
GEMINI_MODEL=

# Backup Settings
BACKUP_ENABLED=true
BACKUP_INTERVAL=24  # hours
"""
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("Created .env template")

def create_directories():
    """Create necessary application directories."""
    try:
        dirs = [
            CONFIG['doc_folder'],
            CONFIG['model_folder'],
            CONFIG['cache_dir'],
            os.path.join(CONFIG['cache_dir'], 'backup')
        ]
        
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"Created directory: {dir_path}")
    except Exception as e:
        print(f"Error creating directories: {e}")
        raise

def setup_logging():
    """Configure logging with file and console handlers."""
    try:
        log_file = os.path.join(CONFIG['cache_dir'], 'chatbot.log')
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logger = logging.getLogger(__name__)
        logger.info("Logging configured successfully")
    except Exception as e:
        print(f"Error configuring logging: {e}")
        raise

def validate_api_key() -> bool:
    """Validate that API key is properly set."""
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_google_api_key_here':
        print("API key not configured")
        return False
    return True

def get_project_root() -> str:
    """Return the project root directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize_app() -> Dict[str, Any]:
    """Initialize all necessary components for the application."""
    try:
        # Setup basic requirements
        create_directories()
        setup_env()
        setup_nltk()
        setup_logging()
        
        if not validate_api_key():
            raise ValueError("Please configure GOOGLE_API_KEY in .env file")
            
        # Import here to avoid circular imports
        from .cache import setup_cache, backup_cache
        from .llm import setup_gemini
        from .embeddings import Model2VecEmbedder
        
        # Setup components
        setup_cache()
        backup_cache()
        model = setup_gemini()
        embedder = Model2VecEmbedder(CONFIG['model_name'])
        
        return {
            'config': CONFIG,
            'embedder': embedder,
            'model': model
        }
    except Exception as e:
        print(f"Error initializing application: {e}")
        raise

def format_response(response: str) -> str:
    """Format bot response for display."""
    return response.strip()