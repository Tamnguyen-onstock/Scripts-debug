import requests
import json
import pandas as pd
import time

def chat_with_model(prompt):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "local-model",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 5000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        return f"Error: {str(e)}"

def run_model(content):
    prompt = f"""
    Trả lời nội dung sau bằng tiếng việt:
    Nội dung:
    {content}
    """
    # prompt = prompt.format(content=content)
    return chat_with_model(prompt)

def main():
    print("Đang kết nối tới LM Studio server...")
    # content = str(input("Nhập nội dung cần phân tích: "))
    content = f"""
    Trả lời câu hỏi bằng tiếng việt:
    xin chào giới thiệu 1 số chức năng của bạn
"""
    # Đọc dữ liệu cần phân tích           
    analysis = run_model(content)
    print(f"Analysis: {analysis}")
    

if __name__ == "__main__":
    main()