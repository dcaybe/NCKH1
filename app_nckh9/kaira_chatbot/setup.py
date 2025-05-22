import nltk
import os
import logging
import json
import shutil
import pickle
import numpy as np
import faiss
import torch
import threading
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
from transformers import AutoTokenizer, AutoModel
import google.generativeai as genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from docx import Document
from nltk.tokenize import sent_tokenize

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load hoặc tạo file config.json với cấu hình mặc định"""
    default_config = {
        "doc_folder": "doc/",
        "model_folder": "model2vec/",
        "model_name": "sentence-transformers/all-MiniLM-L6-v2",
        "cache_dir": "cache/",
        "top_k": 5,
        "chunk_size": 800,
        "min_text_length": 30,
        "max_workers": 8,
        "faiss_nlist": 10,
        "conversation_db": "cache/conversations.db",
        "max_context_messages": 5,
        "llm_cache_size": 1000,
        "batch_size": 64,
        "embedding_cache_size": 10000,
        "embedding_cache_file": "cache/embedding_cache.pkl",
        "retry_attempts": 3,
        "retry_delay": 1
    }
    
    if not os.path.exists('config.json'):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
            logger.info("Đã tạo file config.json với cấu hình mặc định")
        return default_config
        
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Load config mặc định
CONFIG = load_config()


def setup_nltk():
    """Tải các resource cần thiết từ NLTK"""
    try:
        logger.info("Đang tải NLTK resources...")
        nltk.download('punkt', quiet=True)
        logger.info("Đã tải xong NLTK resources")
    except Exception as e:
        logger.error(f"Lỗi khi tải NLTK resources: {e}")
        raise

def setup_env():
    """Tạo file .env template nếu chưa tồn tại"""
    if not os.path.exists('.env'):
        env_content = """# API Keys
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-pro

# Backup Settings
BACKUP_ENABLED=true
BACKUP_INTERVAL=24  # hours
"""
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        logger.info("Đã tạo file .env template")

def setup_model(config: Dict[str, Any]):
    """Tải và kiểm tra model embeddings"""
    try:
        logger.info(f"Kiểm tra model {config['model_name']}...")
        AutoTokenizer.from_pretrained(config['model_name'], cache_dir=config['cache_dir'])
        AutoModel.from_pretrained(config['model_name'], cache_dir=config['cache_dir'])
        logger.info("Đã tải xong model embeddings")
    except Exception as e:
        logger.error(f"Lỗi khi tải model embeddings: {e}")
        raise

def create_directories(config: Dict[str, Any]):
    """Tạo các thư mục cần thiết cho ứng dụng"""
    try:
        for dir in [config['doc_folder'], config['model_folder'], config['cache_dir']]:
            if not os.path.exists(dir):
                os.makedirs(dir)
                logger.info(f"Đã tạo thư mục {dir}")
        
        # Tạo thư mục backup
        backup_dir = os.path.join(config['cache_dir'], 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            logger.info("Đã tạo thư mục backup")
    except Exception as e:
        logger.error(f"Lỗi khi tạo thư mục: {e}")
        raise

def get_cache_key(prompt: str) -> str:
    """Generate cache key for LLM response."""
    return hashlib.md5(prompt.encode()).hexdigest()

def get_cached_response(prompt: str, config: Dict[str, Any]) -> Optional[str]:
    """Get cached LLM response if available."""
    try:
        llm_cache_path = os.path.join(config['cache_dir'], 'llm_cache.pkl')
        with open(llm_cache_path, 'rb') as f:
            cache = pickle.load(f)
        return cache.get(get_cache_key(prompt))
    except Exception:
        return None

def cache_response(prompt: str, response: str, config: Dict[str, Any]) -> None:
    """Cache LLM response for future use."""
    try:
        llm_cache_path = os.path.join(config['cache_dir'], 'llm_cache.pkl')
        with open(llm_cache_path, 'rb') as f:
            cache = pickle.load(f)
        
        # Implement LRU-style cache
        if len(cache) >= config['llm_cache_size']:
            keys = list(cache.keys())
            for _ in range(len(cache) - config['llm_cache_size'] + 1):
                del cache[keys.pop(0)]
                
        cache[get_cache_key(prompt)] = response
        
        with open(llm_cache_path, 'wb') as f:
            pickle.dump(cache, f)
    except Exception as e:
        logger.error(f"Error caching response: {e}")

def setup_cache(config: Dict[str, Any]):
    """Khởi tạo các file cache cần thiết"""
    try:
        # Tạo embedding cache file
        if not os.path.exists(config['embedding_cache_file']):
            with open(config['embedding_cache_file'], 'wb') as f:
                pickle.dump({}, f)
            logger.info("Đã tạo embedding cache file")
            
        # Tạo LLM cache file
        llm_cache = os.path.join(config['cache_dir'], 'llm_cache.pkl')
        if not os.path.exists(llm_cache):
            with open(llm_cache, 'wb') as f:
                pickle.dump({}, f)
            logger.info("Đã tạo LLM cache file")
            
        # Tạo conversation database
        if not os.path.exists(config['conversation_db']):
            import sqlite3
            conn = sqlite3.connect(config['conversation_db'])
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
            logger.info("Đã tạo conversation database")
    except Exception as e:
        logger.error(f"Lỗi khi khởi tạo cache: {e}")
        raise

def backup_cache(config: Dict[str, Any]):
    """Tạo backup cho các file cache quan trọng"""
    try:
        backup_dir = os.path.join(config['cache_dir'], 'backup')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files_to_backup = [
            config['embedding_cache_file'],
            os.path.join(config['cache_dir'], 'llm_cache.pkl'),
            config['conversation_db']
        ]
        
        for file in files_to_backup:
            if os.path.exists(file):
                filename = os.path.basename(file)
                backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
                shutil.copy2(file, backup_path)
                
        logger.info("Đã tạo backup cho các file cache")
    except Exception as e:
        logger.error(f"Lỗi khi tạo backup: {e}")
        logger.warning("Tiếp tục setup mà không có backup")

def setup_gemini():
    """Thiết lập và kiểm tra Google Gemini API"""
    try:
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        logger.info("Đã thiết lập Gemini API thành công")
        return model
    except Exception as e:
        logger.error(f"Lỗi khi thiết lập Gemini API: {e}")
        raise

class Model2VecEmbedder:
    """Singleton class cho model embeddings"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, model_name: str):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self, model_name: str):
        if not hasattr(self, 'model'):
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=CONFIG['cache_dir'])
                self.model = AutoModel.from_pretrained(model_name, cache_dir=CONFIG['cache_dir'])
                self.model.eval()
                if torch.cuda.is_available():
                    self.model = self.model.cuda()
                self.dimension = 384
                self.batch_size = CONFIG['batch_size']
                logger.info(f"Model loaded successfully. Using {'CUDA' if torch.cuda.is_available() else 'CPU'}")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                raise

    @torch.no_grad()
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts"""
        try:
            inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            outputs = self.model(**inputs)
            return outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        except Exception as e:
            logger.error(f"Error embedding batch: {e}")
            raise

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embeddings = self.embed_batch([text])
        return embeddings[0]

def build_or_load_index(texts: List[str], config: Dict[str, Any]) -> Tuple[faiss.Index, List[str], np.ndarray]:
    """Build or load FAISS index with batched processing"""
    index_path = os.path.join(config['cache_dir'], 'faiss.index')
    vectors_path = os.path.join(config['cache_dir'], 'vectors.npy')
    texts_path = os.path.join(config['cache_dir'], 'texts.pkl')
    
    if all(os.path.exists(p) for p in [index_path, vectors_path, texts_path]):
        try:
            logger.info("Loading FAISS index from cache...")
            with open(texts_path, 'rb') as f:
                cached_texts = pickle.load(f)
            vectors = np.load(vectors_path)
            index = faiss.read_index(index_path)
            if torch.cuda.is_available():
                res = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
            logger.info("Đã tải FAISS index từ cache")
            return index, cached_texts, vectors
        except Exception as e:
            logger.error(f"Error loading index from cache: {e}")

    logger.info("Building new FAISS index...")
    try:
        embedder = Model2VecEmbedder(config['model_name'])
        vectors = []
        for i in range(0, len(texts), embedder.batch_size):
            batch = texts[i:i + embedder.batch_size]
            batch_vectors = embedder.embed_batch(batch)
            vectors.append(batch_vectors)
        vectors = np.vstack(vectors).astype('float32')

        # Sử dụng IndexFlatL2 cho tập dữ liệu nhỏ
        index = faiss.IndexFlatL2(embedder.dimension)

        if torch.cuda.is_available():
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)

        index.add(vectors)
        
        # Save to cache
        if torch.cuda.is_available():
            index = faiss.index_gpu_to_cpu(index)
        faiss.write_index(index, index_path)
        np.save(vectors_path, vectors)
        with open(texts_path, 'wb') as f:
            pickle.dump(texts, f)
            
        if torch.cuda.is_available():
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index)
        
        logger.info("Đã tạo và lưu FAISS index mới")
        return index, texts, vectors
    except Exception as e:
        logger.error(f"Error building index: {e}")
        raise

def process_document(file_path: str, queue: Queue) -> None:
    """Process a .docx file with optimized chunk creation."""
    try:
        doc = Document(file_path)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in doc.paragraphs:
            text = para.text.strip()
            if len(text) < CONFIG['min_text_length']:
                continue
                
            sentences = sent_tokenize(text)
            for sentence in sentences:
                if current_length + len(sentence.split()) <= CONFIG['chunk_size']:
                    current_chunk.append(sentence)
                    current_length += len(sentence.split())
                else:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence.split())
                    
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        queue.put((file_path, chunks))
        logger.info(f"Processed file {file_path}: {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        queue.put((file_path, []))

def load_documents(folder: str) -> List[str]:
    """Load and process .docx files with parallel processing."""
    docx_files = [f for f in os.listdir(folder) if f.endswith(".docx")]
    if not docx_files:
        logger.error(f"No .docx files found in {folder}")
        raise ValueError("No .docx files found")
    
    chunks = []
    queue = Queue()
    
    with ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
        futures = []
        for fname in docx_files:
            file_path = os.path.join(folder, fname)
            futures.append(executor.submit(process_document, file_path, queue))
        
        for future in as_completed(futures):
            future.result()
    
    while not queue.empty():
        _, file_chunks = queue.get()
        chunks.extend(file_chunks)
    
    if not chunks:
        logger.warning("No content found in .docx files")
    else:
        logger.info(f"Loaded {len(chunks)} text chunks")
    
    return chunks

def auto_setup():
    """Chạy toàn bộ quá trình setup"""
    try:
        logger.info("Bắt đầu quá trình setup...")
        
        # Load hoặc tạo config
        config = load_config()
        
        # Thực hiện các bước setup
        create_directories(config)
        setup_env()
        setup_nltk()
        setup_model(config)
        setup_cache(config)
        backup_cache(config)
        
        # Thiết lập các components
        setup_gemini()
        embedder = Model2VecEmbedder(config['model_name'])
        
        logger.info("Setup hoàn tất!")
        # Khởi tạo Gemini model và trả về
        model = setup_gemini()
        return config, embedder, model
    except Exception as e:
        logger.error(f"Lỗi trong quá trình setup: {e}")
        raise

if __name__ == "__main__":
    auto_setup()