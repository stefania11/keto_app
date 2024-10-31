import os
import requests

def test_deepseek_api():
    api_key = os.getenv('deepseek_api')
    if not api_key:
        print("DeepSeek API key not found in environment variables")
        return

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
        print("API test successful")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"API test failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")

if __name__ == "__main__":
    test_deepseek_api()
