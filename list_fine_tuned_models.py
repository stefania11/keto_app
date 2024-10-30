import os
from openai import OpenAI
import json

def list_fine_tuned_models():
    """List all available fine-tuned models."""
    print("\nListing available fine-tuned models...")

    # Initialize client with cleaned credentials
    client = OpenAI(
        api_key=os.environ.get('OAI_key').strip(),
        organization=os.environ.get('OAI_organization_id').strip()
    )

    try:
        # List all models
        models = client.models.list()

        # Filter for fine-tuned models
        fine_tuned_models = [
            model for model in models.data
            if model.id.startswith('ft:')
        ]

        if fine_tuned_models:
            print("\nAvailable fine-tuned models:")
            for model in fine_tuned_models:
                print(f"\nModel ID: {model.id}")
                print(f"Created: {model.created}")
                print(f"Owned by: {model.owned_by}")
                print("-" * 50)
        else:
            print("\nNo fine-tuned models found.")

        # Save models to file for reference
        with open('available_fine_tuned_models.json', 'w') as f:
            json.dump(
                [model.model_dump() for model in fine_tuned_models],
                f,
                indent=2
            )
            print("\nModel details saved to available_fine_tuned_models.json")

    except Exception as e:
        print(f"\nError listing models: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    list_fine_tuned_models()
