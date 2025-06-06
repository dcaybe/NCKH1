import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
sys.stdout.reconfigure(encoding='utf-8')
import logging
import numpy as np
import faiss
import torch
import shutil
from datetime import datetime
from docx import Document
from dotenv import load_dotenv
from src.config import CONFIG
from src.utils import setup_nltk, setup_env, create_directories
from src.cache import setup_cache, backup_cache
from src.embeddings import Model2VecEmbedder
from src.llm import setup_gemini
from src.document import load_documents

def auto_setup():
    """Chạy toàn bộ quá trình setup"""
    try:
        # 1. Thiết lập logging cơ bản
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
        logger = logging.getLogger(__name__)
        
        logger.info("Bắt đầu quá trình setup...")
        
        # 2. Tạo các thư mục cần thiết
        logger.info("Tạo cấu trúc thư mục...")
        create_directories()
        
        # 3. Tạo file .env template
        logger.info("Thiết lập file môi trường...")
        setup_env()
        
        # 4. Tải NLTK resources
        logger.info("Tải NLTK resources...")
        setup_nltk()
        
        # 5. Thiết lập và test model embeddings
        logger.info(f"Kiểm tra model {CONFIG['model_name']}...")
        try:
            model = Model2VecEmbedder(CONFIG['model_name'])
            # Test embeddings
            test_text = "Kiểm tra embedding model"
            embeddings = model.embed(test_text)
            assert embeddings.shape == (model.dimension,), "Embedding dimension không đúng"
            logger.info("Model embeddings hoạt động tốt")
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra model: {e}")
            raise
            
        # 6. Thiết lập cache
        logger.info("Khởi tạo cache...")
        setup_cache()
        
        # 7. Backup dữ liệu hiện có
        logger.info("Tạo backup...")
        backup_cache()
        
        # 8. Test tính năng xử lý document và di chuyển model
        logger.info("Kiểm tra xử lý document và di chuyển model...")
        
        # Di chuyển model từ cache vào thư mục model
        cache_model_path = os.path.join(
            CONFIG['cache_dir'],
            'models--sentence-transformers--all-MiniLM-L6-v2'
        )
        if os.path.exists(cache_model_path):
            model_name = CONFIG['model_name'].replace('/', '_')
            target_path = os.path.join(CONFIG['model_folder'], model_name)
            if not os.path.exists(target_path):
                os.makedirs(target_path)
            
            # Copy các file cần thiết
            for item in os.listdir(cache_model_path):
                if item == 'blobs':
                    src = os.path.join(cache_model_path, item)
                    dst = os.path.join(target_path, item)
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            logger.info("Đã sao chép model vào thư mục model")
        
        # Kiểm tra xử lý document
        if os.path.exists(CONFIG['doc_folder']) and os.listdir(CONFIG['doc_folder']):
            try:
                texts = load_documents(CONFIG['doc_folder'])
                logger.info(f"Đã xử lý {len(texts)} đoạn văn bản")
            except Exception as e:
                logger.error(f"Lỗi khi test xử lý document: {e}")
                logger.warning("Bạn cần thêm tài liệu vào thư mục doc/")
        else:
            logger.warning("Chưa có tài liệu trong thư mục doc/")
        
        # 9. Kiểm tra kết nối Gemini API
        if os.path.exists('.env'):
            logger.info("Kiểm tra Gemini API...")
            try:
                llm_model = setup_gemini()
                # Test generation
                response = llm_model.generate_content("Xin chào")
                assert response.text, "Không nhận được phản hồi từ Gemini API"
                logger.info("Kết nối Gemini API thành công!")
            except Exception as e:
                logger.warning(f"Chưa thiết lập Gemini API: {e}")
                logger.warning("Bạn cần cấu hình GOOGLE_API_KEY trong file .env")
        else:
            logger.warning("Chưa có file .env. Bạn cần tạo và cấu hình GOOGLE_API_KEY")
        
        # 10. Test backup và restore
        logger.info("Kiểm tra backup/restore...")
        try:
            backup_cache()  # Tạo backup mới
            backup_dir = os.path.join(CONFIG['cache_dir'], 'backup')
            assert os.path.exists(backup_dir), "Thư mục backup không tồn tại"
            backup_files = os.listdir(backup_dir)
            assert len(backup_files) > 0, "Không có file backup"
            logger.info("Chức năng backup hoạt động tốt")
        except Exception as e:
            logger.error(f"Lỗi khi test backup: {e}")
        
        logger.info("Hoàn tất quá trình cài đặt!")
        logger.info("Chạy 'python app.py hoặc run.bat' để khởi động ứng dụng")
        
    except Exception as e:
        logger.error(f"Lỗi trong quá trình cài đặt: {e}")
        raise

if __name__ == "__main__":
    auto_setup()