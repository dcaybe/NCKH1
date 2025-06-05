import os
import logging
import threading
import torch
import numpy as np
import faiss
import pickle
from typing import List, Tuple
from transformers import AutoTokenizer, AutoModel
from .config import CONFIG

logger = logging.getLogger(__name__)

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
                # Tải model với cache_dir và lưu vào model_folder
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=CONFIG['cache_dir'],
                    local_files_only=False
                )
                self.model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=CONFIG['cache_dir'],
                    local_files_only=False
                )
                
                # Lưu model vào thư mục model
                os.makedirs(CONFIG['model_folder'], exist_ok=True)
                model_path = os.path.join(CONFIG['model_folder'], model_name.replace('/', '_'))
                self.tokenizer.save_pretrained(model_path)
                self.model.save_pretrained(model_path)
                
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

def build_or_load_index(texts: List[str], config: dict) -> Tuple[faiss.Index, List[str], np.ndarray]:
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

def retrieve(query: str, embedder: Model2VecEmbedder, index: faiss.Index, texts: List[str], top_k: int = None) -> List[str]:
    """Retrieve relevant text chunks with optimized search."""
    if top_k is None:
        top_k = CONFIG['top_k']
    try:
        q_vec = embedder.embed(query).astype('float32').reshape(1, -1)
        D, I = index.search(q_vec, top_k)
        results = []
        seen = set()  # Avoid duplicate chunks
        for i in I[0]:
            if i < len(texts) and texts[i] not in seen:
                results.append(texts[i])
                seen.add(texts[i])
        logger.debug(f"Found {len(results)} unique results for query")
        return results
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return []