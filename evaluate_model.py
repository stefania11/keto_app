import json
import openai
from openai import OpenAI
import numpy as np
from sklearn.metrics import accuracy_score, mean_squared_error
import os

# Set up the OpenAI client
client = OpenAI()

# Load the test dataset
def load_test_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Prepare a single example for evaluation
def prepare_example(project):
    return f"Describe the structure of this Scratch project with ID {project['project_id']}."

# Generate a response using the fine-tuned model
def generate_response(prompt, model_name):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that understands Scratch projects and can describe their structure."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

# Evaluate the model's performance
def evaluate_model(test_data, model_name):
    predictions = []
    actual = []

    for project in test_data:
        prompt = prepare_example(project)
        response = generate_response(prompt, model_name)

        # Simple accuracy metric: check if all block names are mentioned in the response
        block_names = [block['name'] for block in project['blocks']]
        prediction = all(name.lower() in response.lower() for name in block_names)

        predictions.append(prediction)
        actual.append(1)  # Assuming all test examples should be correctly described

    accuracy = accuracy_score(actual, predictions)
    mse = mean_squared_error(actual, predictions)

    return accuracy, mse

# Main execution
if __name__ == "__main__":
    # Set the API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Load test data
    test_data = load_test_data('sampled_projects.json')[:10]  # Using a small subset for quick evaluation

    # Fine-tuned model name
    model_name = "ft:gpt-4o-mini-2024-07-18:personal::AE2IkhGQ"

    # Evaluate the model
    accuracy, mse = evaluate_model(test_data, model_name)

    print(f"Model Evaluation Results:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"Mean Squared Error: {mse:.2f}")
