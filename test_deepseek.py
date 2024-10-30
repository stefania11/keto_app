import os
import requests
import json
from time import sleep

def test_deepseek_api():
    api_key = os.environ.get('deepseek_api')
    if not api_key:
        print("DeepSeek API key not found in environment variables")
        return False

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Simplified test request
    test_data = {
        "model": "deepseek-coder",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you help me analyze some code?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    print("Testing DeepSeek API connection...")
    print(f"Request URL: {url}")
    print(f"Request Headers: {json.dumps(headers, indent=2)}")
    print(f"Request Data: {json.dumps(test_data, indent=2)}\n")

    try:
        # Set a shorter timeout
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")

        if response.status_code == 200:
            result = response.json()
            print("\nAPI Response:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Response Content: {response.text}")
            print(f"\nAPI call failed with status code: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("\nRequest timed out after 10 seconds")
        return False
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_deepseek_api()
