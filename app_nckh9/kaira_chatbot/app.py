import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['PYTORCH_JIT'] = '0'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

import sys
import re
import torch
torch.set_grad_enabled(False)

from src import (
    CONFIG,
    load_documents, build_or_load_index,
    retrieve, create_prompt, ask_llm, save_conversation,
    is_greeting, get_greeting_response,
    format_no_context_message, initialize_app
)

def remove_markdown(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'_(.*?)_', r'\1', text)        # Underline
    return text

def process_question(question, components, index, texts):
    try:
        if is_greeting(question):
            response = get_greeting_response()
        else:
            contexts = retrieve(
                question,
                components['embedder'],
                index,
                texts
            )
            
            if not contexts:
                response = format_no_context_message()
            else:
                prompt = create_prompt(question, contexts)
                response = ask_llm(prompt, components['model'])
        
        response = remove_markdown(response)
        save_conversation(question, response)
        return response
    except Exception as e:
        return f"Lỗi: {str(e)}"

def main():
    try:
        # Khởi tạo components và load documents chỉ một lần
        components = initialize_app()
        print("\n=== Chatbot HỎI ĐÁP TÀI LIỆU ===\n")
        
        # Load documents và index một lần duy nhất
        print("Đang tải dữ liệu...")
        texts = load_documents(CONFIG['doc_folder'])
        index, texts, _ = build_or_load_index(texts, CONFIG)
        print("Đã tải xong dữ liệu!\n")
        
        while True:
            question = input("\nHỏi: ").strip()
            if not question:
                continue
                
            if question.lower() in ['quit', 'exit', 'thoát']:
                print("\nTạm biệt!\n")
                break
                
            response = process_question(question, components, index, texts)
            print("\nBot:", response, "\n")
                
    except Exception as e:
        print(f"\nLỗi khởi tạo chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()