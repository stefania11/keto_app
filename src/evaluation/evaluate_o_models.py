# Import required libraries
import os
import json
from openai import OpenAI
from datetime import datetime
import time

def evaluate_o_models():
    client = OpenAI(
        api_key=os.environ['OAI_key'],
        organization=os.environ['OAI_organization_id']
    )
    
    # Load test data (5 samples)
    with open('standardized_training_data.jsonl', 'r') as f:
        all_data = [json.loads(line) for line in f][:5]

    # Models to evaluate
    models = ['gpt-4o', 'o1-preview', 'o1-mini']
    results = []

    for model in models:
        print(f'\nEvaluating {model}...')
        model_results = evaluate_model(client, model, all_data)
        results.append(model_results)

    # Save and print results
    save_results(results)

def evaluate_model(client, model, test_data):
    model_results = []
    for test_item in test_data:
        result = process_single_test(client, model, test_item)
        model_results.append(result)
    return calculate_model_metrics(model, model_results)

def process_single_test(client, model, test_item):
    try:
        response = get_model_response(client, model, test_item)
        metrics = calculate_metrics(response, test_item['completion'])
        return {
            'prompt': test_item['prompt'],
            'response': response,
            'metrics': metrics
        }
    except Exception as e:
        return {'error': str(e)}

def get_model_response(client, model, test_item):
    messages = [
        {
            'role': 'system',
            'content': 'Format: " blocks:\nsprite: Name1\nsprite: Name2"'
        },
        {
            'role': 'user',
            'content': test_item['prompt']
        }
    ]
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return completion.choices[0].message.content.strip()

def calculate_metrics(response, expected):
    # Calculate format checks and semantic similarity
    format_check = check_format(response)
    similarity = calculate_similarity(response, expected)
    return {
        'format_check': format_check,
        'semantic_similarity': similarity
    }

def save_results(results):
    output_file = f'o_series_evaluation_{datetime.now().isoformat()}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'Results saved to {output_file}')

if __name__ == "__main__":
    evaluate_o_models()
