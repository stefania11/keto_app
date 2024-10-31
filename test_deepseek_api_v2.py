import os
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_deepseek_api():
    api_key = os.getenv('deepseek_api')
    if not api_key:
        raise ValueError("DeepSeek API key not found")

    # Configure session with retries
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert at analyzing code."
            },
            {
                "role": "user",
                "content": "What is 2+2?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        logging.info("Sending test request to DeepSeek API...")
        response = session.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )

        logging.info(f"Response status code: {response.status_code}")
        logging.info(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")

        if response.status_code != 200:
            logging.error(f"Error response: {response.text}")
            return False

        response_json = response.json()
        logging.info(f"Response content: {json.dumps(response_json, indent=2)}")

        completion = response_json["choices"][0]["message"]["content"]
        logging.info(f"Generated completion: {completion}")

        return True

    except Exception as e:
        logging.error(f"Error testing API: {str(e)}")
        if isinstance(e, requests.exceptions.RequestException) and hasattr(e, 'response'):
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
        return False

if __name__ == "__main__":
    print("Testing DeepSeek API connection...")
    success = test_deepseek_api()
    print(f"Test {'succeeded' if success else 'failed'}")
