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

        # Refined accuracy metric: check for partial matches and consider structure
        block_names = [block['name'].lower() for block in project['blocks']]
        block_types = [block['type'].lower() for block in project['blocks']]

        # Check for block names
        name_matches = sum(name in response.lower() for name in block_names)
        name_accuracy = name_matches / len(block_names) if block_names else 1.0

        # Check for block types
        type_matches = sum(type_ in response.lower() for type_ in block_types)
        type_accuracy = type_matches / len(block_types) if block_types else 1.0

        # Check for structure keywords
        structure_keywords = ['structure', 'contains', 'consists of', 'composed of']
        structure_score = any(keyword in response.lower() for keyword in structure_keywords)

        # Combine scores
        prediction = (name_accuracy * 0.4 + type_accuracy * 0.4 + structure_score * 0.2)

        predictions.append(prediction)
        actual.append(1)  # Assuming all test examples should be correctly described

    accuracy = np.mean(predictions)  # Use mean of predictions as overall accuracy
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
