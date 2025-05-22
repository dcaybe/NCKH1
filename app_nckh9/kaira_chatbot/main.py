import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime
import logging
import sys
import numpy as np
import faiss
import torch
from queue import Queue
from typing import List, Dict, Any, Tuple, Optional
from docx import Document
from nltk.tokenize import sent_tokenize
import re
from tenacity import retry, stop_after_attempt, wait_exponential
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import từ setup.py
from setup import (
    CONFIG, Model2VecEmbedder, setup_gemini, build_or_load_index,
    get_cache_key, get_cached_response, cache_response,
    load_documents, process_document, auto_setup
)

# === LOGGING SETUP ===
# Thiết lập logging chỉ ghi vào file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Lưu trữ components toàn cục
CONFIG, EMBEDDER, GEMINI_MODEL = auto_setup()

# === BLACKLIST KEYWORDS ===
BLACKLIST_KEYWORDS = [
    "tục tĩu", "sex", "xxx", "bậy", "ngu", "đồ ngu", "chửi", "mẹ mày",
    "địt", "lồn", "cặc", "buồi", "đm", "đcm", "vcl", "vl"
]

# === INDEX OPERATIONS ===
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

# === OPTIMIZED LLM INTERACTION ===
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def ask_llm(prompt: str) -> str:
    """Call Gemini API with enhanced response quality control."""
    cached_response = get_cached_response(prompt, CONFIG)
    if cached_response:
        logger.debug("Using cached response")
        return cached_response

    try:
        # Sử dụng model đã được khởi tạo
        model = GEMINI_MODEL
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 2048,
            "stop_sequences": ["Người dùng:", "Human:", "Assistant:"],
            "candidate_count": 1
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if not response.text:
            return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."
            
        # Post-process response
        answer = response.text.strip()
        
        # Ensure reasonable length
        if len(answer.split()) > 200:  # Khoảng 10-15 câu
            paragraphs = answer.split('\n\n')
            answer = '\n\n'.join(paragraphs[:3])  # Giữ 3 đoạn văn đầu tiên
            answer += "\n\n(Đã tóm tắt nội dung chính)"
        
        # Cache processed response
        cache_response(prompt, answer, CONFIG)
        return answer
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise

            

# === CONTENT FILTERING ===
def filter_sensitive_content(query: str) -> Tuple[bool, str]:
    """Enhanced content filtering with regex patterns."""
    query_lower = query.lower()
    
    # Kiểm tra từng từ khóa với regex
    for keyword in BLACKLIST_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
            logger.warning(f"Phát hiện nội dung không phù hợp")
            return False, "Xin lỗi, câu hỏi của bạn chứa nội dung không phù hợp. Vui lòng đặt câu hỏi khác."
    
    return True, ""

# === MAIN CHAT FUNCTION ===
def get_chatbot_response(query: str) -> str:
    """Get AI assistant response for admin interface."""
    try:
        # Load documents and build index if not exists
        texts = load_documents(CONFIG['doc_folder'])
        index, _, _ = build_or_load_index(texts, CONFIG)
        
        # Get response from chat function
        response = chat(query, EMBEDDER, index, texts)
        
        if not response:
            return "Xin lỗi, tôi không thể tạo câu trả lời lúc này."
            
        return response
        
    except Exception as e:
        logger.error(f"Error getting chatbot response: {e}")
        return "Có lỗi xảy ra khi xử lý yêu cầu của bạn."

def chat(query: str, embedder: Model2VecEmbedder, index: faiss.Index, texts: List[str]) -> str:
    """Optimized chat function with greeting detection."""
    try:
        # Kiểm tra nội dung
        is_appropriate, message = filter_sensitive_content(query)
        if not is_appropriate:
            return message

        # Kiểm tra nếu là lời chào
        query_lower = query.lower()
        greetings = ["xin chào", "hello", "hi", "chào", "hey"]
        if any(greeting in query_lower for greeting in greetings):
            return "Xin chào! Tôi là trợ lý AI được tạo ra để hỗ trợ trả lời các câu hỏi về thông tin trong tài liệu. Bạn có thể hỏi bất kỳ thông tin gì và tôi sẽ cố gắng giúp đỡ bạn."

        # Tìm kiếm thông tin liên quan
        contexts = retrieve(query, embedder, index, texts)
        if not contexts:
            return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu được cung cấp."

        # Tạo prompt với template tối ưu
        prompt = f"""Vai trò: Bạn là một trợ lý AI chuyên nghiệp, thông minh và hữu ích.

Thông tin tham khảo từ tài liệu:
{' '.join(contexts)}

Câu hỏi hiện tại: {query}

Yêu cầu:
1. Trả lời bằng tiếng Việt, rõ ràng và dễ hiểu
2. Đảm bảo câu trả lời:
   - Chính xác và phù hợp với thông tin trong tài liệu
   - Ngắn gọn, súc tích (tối đa 3-4 câu cho mỗi ý chính)
   - Có cấu trúc rõ ràng nếu cần liệt kê nhiều điểm
3. Không thêm thông tin ngoài tài liệu tham khảo

Trả lời:"""

        # Gọi API
        answer = ask_llm(prompt)
        return answer

    except Exception as e:
        logger.error(f"Lỗi trong quá trình xử lý: {e}")
        return "Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn."

# === MAIN ===
def main():
    """Optimized main function with better error handling."""
    try:

        logger.info("Đọc tài liệu...")
        texts = load_documents(CONFIG['doc_folder'])
        if not texts:
            logger.error(f"Không tìm thấy nội dung hợp lệ trong {CONFIG['doc_folder']}")
            raise ValueError("Không tìm thấy nội dung hợp lệ")

        logger.info("Khởi tạo FAISS index...")
        index, texts, _ = build_or_load_index(texts, CONFIG)

        print("\nSẵn sàng trò chuyện! Gõ 'exit' để thoát.")

        while True:
            try:
                query = input("\nHãy đặt câu hỏi: ").strip()
                if query.lower() in ["exit", "quit"]:
                    break
                if not query:
                    continue

                answer = chat(query, EMBEDDER, index, texts)
                print(f"\n{answer}")

            except KeyboardInterrupt:
                print("\nĐang thoát chương trình...")
                break
            except Exception as e:
                logger.error(f"Lỗi: {e}")
                print("\nCó lỗi xảy ra, vui lòng thử lại.")

    except Exception as e:
        logger.error(f"Lỗi khởi tạo: {e}")
        print("Có lỗi xảy ra khi khởi tạo chương trình.")

if __name__ == "__main__":
    main()