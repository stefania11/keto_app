import os
from openai import OpenAI
import json

def test_model_access(model_id):
    """Test if we can access the specified model."""
    print(f"\nTesting access to model: {model_id}")

    # Initialize client with cleaned credentials
    client = OpenAI(
        api_key=os.environ.get('OAI_key').strip(),
        organization=os.environ.get('OAI_organization_id').strip()
    )

    try:
        # First, try to list models to verify API access
        print("Checking API access...")
        models = client.models.list()
        print("Successfully connected to OpenAI API")

        # Try a simple completion with the model
        print(f"\nTesting model completion...")
        messages = [
            {"role": "system", "content": "You analyze Scratch projects and describe their structure."},
            {"role": "user", "content": "Describe Scratch project ID 99578106."}
        ]

        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )

        print("\nSuccessfully got response from model:")
        print(json.dumps(response.model_dump(), indent=2))
        return True

    except Exception as e:
        print(f"\nError accessing model: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    model_id = "ft:gpt-4-0613:personal::8K2glPZx"
    test_model_access(model_id)
