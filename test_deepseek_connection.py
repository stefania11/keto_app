import os
import requests

def test_deepseek_connection():
    api_key = os.getenv('deepseek_api')
    if not api_key:
        print("DeepSeek API key not found in environment variables")
        return False

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-coder-v2",
        "messages": [{"role": "user", "content": "Hello, world!"}],
        "temperature": 0.7,
        "max_tokens": 10
    }

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        print("DeepSeek API connection successful")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"DeepSeek API connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_connection()
