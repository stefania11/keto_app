import requests
import json
import os

def list_available_models():
    api_key = os.environ.get('deepseek_api')
    if not api_key:
        print("DeepSeek API key not found in environment variables")
        return

    url = "https://api.deepseek.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    print("Fetching available DeepSeek models...")
    try:
        response = requests.get(url, headers=headers)
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {json.dumps(dict(response.headers), indent=2)}")

        if response.status_code == 200:
            models = response.json()
            print("\nAvailable Models:")
            print(json.dumps(models, indent=2))
        else:
            print(f"Response Content: {json.dumps(response.json() if response.text else {}, indent=2)}")
            print(f"\nFailed to fetch models. Status code: {response.status_code}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")

if __name__ == "__main__":
    list_available_models()
