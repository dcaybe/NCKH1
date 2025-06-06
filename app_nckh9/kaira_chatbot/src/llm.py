import os
import logging
from typing import Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from .config import CONFIG
from .cache import get_cached_response, cache_response

logger = logging.getLogger(__name__)

def setup_gemini():
    """Initialize and configure Google Gemini model."""
    try:
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        logger.info("Initialized Gemini API successfully")
        return model
    except Exception as e:
        logger.error(f"Error initializing Gemini API: {e}")
        raise

def create_prompt(query: str, contexts: list) -> str:
    """Create an optimized prompt for the LLM."""
    return f"""Vai trò: Bạn là một trợ lý AI chuyên nghiệp, thông minh và hữu ích.

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

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def ask_llm(prompt: str, model=None) -> str:
    """Generate response from Gemini with enhanced error handling and retries."""
    if not model:
        model = setup_gemini()

    # Check cache first
    cached_response = get_cached_response(prompt)
    if cached_response:
        logger.debug("Using cached response")
        return cached_response

    try:
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
        cache_response(prompt, answer)
        return answer
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise

def get_greeting_response() -> str:
    """Return a standard greeting response."""
    return "Xin chào! Tôi là trợ lý AI được tạo ra để hỗ trợ trả lời các câu hỏi về thông tin trong tài liệu. Bạn có thể hỏi bất kỳ thông tin gì và tôi sẽ cố gắng giúp đỡ bạn."

def is_greeting(text: str) -> bool:
    """Check if the input text is a greeting."""
    greetings = ["xin chào", "hello", "hi", "chào", "hey"]
    return any(greeting in text.lower() for greeting in greetings)

def format_error_message() -> str:
    """Return a standard error message."""
    return "Xin lỗi, đã xảy ra lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."

def format_no_context_message() -> str:
    """Return a message when no relevant context is found."""
    return "Xin lỗi, tôi không tìm thấy thông tin liên quan trong tài liệu được cung cấp."