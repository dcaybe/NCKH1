import os
import logging
import unicodedata
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from docx import Document
from nltk.tokenize import sent_tokenize
from .config import CONFIG

logger = logging.getLogger(__name__)

def process_document(file_path: str, queue: Queue) -> None:
    """Process a .docx file with optimized chunk creation and proper encoding handling."""
    try:
        doc = Document(file_path)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in doc.paragraphs:
            try:
                # Get text and ensure proper encoding
                text = para.text.strip()
                
                # Handle encoding issues by normalizing text
                if text:
                    # Normalize Unicode text for Vietnamese
                    text = unicodedata.normalize('NFC', text)
                    
                    # Ensure UTF-8 encoding
                    try:
                        text = text.encode('utf-8').decode('utf-8')
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        text = text.encode('utf-8', errors='replace').decode('utf-8')
                    
                    # Clean text
                    text = ' '.join(text.split())  # Remove extra whitespace
                    
                    # If text is already bytes, decode safely
                    if isinstance(text, bytes):
                        text = text.decode('utf-8', errors='ignore')
                
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
            except Exception as para_error:
                logger.warning(f"Error processing paragraph in {file_path}: {para_error}")
                continue
                    
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

def create_document_directories():
    """Create necessary directories for document processing"""
    try:
        for dir in [CONFIG['doc_folder'], CONFIG['model_folder'], CONFIG['cache_dir']]:
            if not os.path.exists(dir):
                os.makedirs(dir)
                logger.info(f"Đã tạo thư mục {dir}")
        
        # Tạo thư mục backup
        backup_dir = os.path.join(CONFIG['cache_dir'], 'backup')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            logger.info("Đã tạo thư mục backup")
    except Exception as e:
        logger.error(f"Lỗi khi tạo thư mục: {e}")
        raise

def filter_sensitive_content(text: str) -> bool:
    """Check if text contains any blacklisted keywords"""
    text_lower = text.lower()
    return not any(keyword in text_lower for keyword in CONFIG['blacklist_keywords'])

def list_documents() -> List[str]:
    """Return list of all documents in the doc folder"""
    if not os.path.exists(CONFIG['doc_folder']):
        return []
    return [f for f in os.listdir(CONFIG['doc_folder']) if f.endswith('.docx')]