import os
import json
from openai import OpenAI
from datetime import datetime
import random
import time
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
import numpy as np
from collections import defaultdict
from tqdm import tqdm

def calculate_semantic_similarity(str1, str2):
    """Calculate semantic similarity between two strings using SequenceMatcher."""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def normalize_sprite_name(name):
    """Normalize sprite names for comparison."""
    return name.lower().strip().replace('-', ' ').replace('_', ' ')

def extract_sprites(text):
    """Extract sprite names from the text while handling various formats."""
    sprites = []
    for line in text.split('\n'):
        if 'sprite:' in line.lower():
            sprite = line.split('sprite:', 1)[1].strip()
            sprites.append(sprite)
    return sprites

def evaluate_response(response, expected):
    """Evaluate a model response using multiple semantic similarity metrics."""
    response_sprites = extract_sprites(response)
    expected_sprites = extract_sprites(expected)

    # Normalize sprite names
    norm_response = [normalize_sprite_name(s) for s in response_sprites]
    norm_expected = [normalize_sprite_name(s) for s in expected_sprites]

    # Calculate various similarity metrics
    metrics = {
        'exact_match': 0,
        'semantic_similarity': 0,
        'partial_match': 0,
        'order_similarity': 0
    }

    # Exact match after normalization
    exact_matches = set(norm_response) & set(norm_expected)
    metrics['exact_match'] = len(exact_matches) / max(len(norm_expected), 1)

    # Semantic similarity using SequenceMatcher
    if norm_expected:
        similarities = []
        for exp_sprite in norm_expected:
            sprite_similarities = [calculate_semantic_similarity(exp_sprite, resp_sprite)
                                 for resp_sprite in norm_response]
            similarities.append(max(sprite_similarities) if sprite_similarities else 0)
        metrics['semantic_similarity'] = sum(similarities) / len(similarities)

    # Partial match (substring matching)
    partial_matches = 0
    for exp_sprite in norm_expected:
        for resp_sprite in norm_response:
            if exp_sprite in resp_sprite or resp_sprite in exp_sprite:
                partial_matches += 1
                break
    metrics['partial_match'] = partial_matches / max(len(norm_expected), 1)

    # Order similarity (sequence alignment)
    if norm_expected and norm_response:
        order_sim = SequenceMatcher(None, norm_response, norm_expected).ratio()
        metrics['order_similarity'] = order_sim

    return metrics

def evaluate_model(client, model_name, model_id, test_data):
    """Evaluate a model using semantic similarity metrics."""
    print(f'\nEvaluating {model_name} ({model_id})...')
    results = []

    # Add progress bar
    pbar = tqdm(test_data, desc=f'Evaluating {model_name}')
    for test_item in pbar:
        try:
            messages = [
                {
                    'role': 'system',
                    'content': '''You are an AI assistant that understands Scratch projects and can describe their structure.
Format Rules:
1. Start with exactly " blocks:" (note the leading space)
2. List each sprite on a new line
3. Each sprite line must start with "sprite: "
4. No extra text or explanations'''
                },
                {
                    'role': 'user',
                    'content': test_item['prompt']
                }
            ]

            # Retry logic with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model=model_id,
                        messages=messages,
                        temperature=0,
                        request_timeout=30  # Add timeout
                    )
                    response = completion.choices[0].message.content.strip()
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    pbar.write(f'Attempt {attempt + 1} failed, retrying...')
                    time.sleep(2 ** attempt)

            expected = test_item['completion'].strip()

            # Evaluate response using semantic metrics
            metrics = evaluate_response(response, expected)

            # Format validation
            format_check = {
                'space_prefix': response.startswith(' blocks:'),
                'blocks_header': ' blocks:' in response,
                'sprite_format': all(line.startswith('sprite: ')
                                   for line in response.split('\n')[1:] if line.strip()),
                'newline_after_header': 'blocks:\n' in response
            }

            result = {
                'prompt': test_item['prompt'],
                'expected': expected,
                'response': response,
                'metrics': metrics,
                'format_check': format_check
            }
            results.append(result)

            # Update progress bar description with current metrics
            pbar.set_description(f'{model_name} - Semantic Sim: {metrics["semantic_similarity"]:.2%}')

        except Exception as e:
            pbar.write(f'Error evaluating prompt {test_item["prompt"]}: {str(e)}')
            results.append({
                'prompt': test_item['prompt'],
                'error': str(e)
            })

    # Calculate aggregate metrics
    valid_results = [r for r in results if 'error' not in r]
    if valid_results:
        aggregates = {
            'exact_match_avg': np.mean([r['metrics']['exact_match'] for r in valid_results]),
            'semantic_similarity_avg': np.mean([r['metrics']['semantic_similarity'] for r in valid_results]),
            'partial_match_avg': np.mean([r['metrics']['partial_match'] for r in valid_results]),
            'order_similarity_avg': np.mean([r['metrics']['order_similarity'] for r in valid_results]),
            'format_accuracy': np.mean([all(r['format_check'].values()) for r in valid_results])
        }
    else:
        aggregates = {metric: 0.0 for metric in ['exact_match_avg', 'semantic_similarity_avg',
                                                'partial_match_avg', 'order_similarity_avg',
                                                'format_accuracy']}

    return {
        'model': model_name,
        'model_id': model_id,
        'results': results,
        'aggregates': aggregates
    }

def main():
    """Main evaluation function with parallel processing."""
    try:
        print('Initializing OpenAI client...')
        client = OpenAI(
            api_key=os.environ['OAI_key'],
            organization=os.environ['OAI_organization_id']
        )

        # Load test data
        print('Loading test data...')
        with open('standardized_training_data.jsonl', 'r') as f:
            all_data = [json.loads(line) for line in f]

        # Select smaller test sample
        test_size = min(5, len(all_data))  # Reduced from 10 to 5
        print(f'Selecting {test_size} test samples...')
        test_data = random.sample(all_data, test_size)

        # Models to evaluate
        models = {
            'gpt-4o': 'ft:gpt-4o-2024-08-06:personal::AEk9dgyk',
            'gpt-4o-mini': 'ft:gpt-4o-mini-2024-07-18:personal::AEREcDGY'
        }

        print(f'Starting evaluation of {len(models)} models...')
        # Sequential evaluation for better progress tracking
        results = []
        for name, model_id in models.items():
            try:
                result = evaluate_model(client, name, model_id, test_data)
                results.append(result)
                print(f'\nCompleted evaluation of {name}')
            except Exception as e:
                print(f'Error evaluating {name}: {str(e)}')

        # Save results
        timestamp = datetime.now().isoformat()
        output_file = f'semantic_evaluation_results_{timestamp}.json'
        print(f'\nSaving results to {output_file}...')
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'models_evaluated': list(models.keys()),
                'test_size': test_size,
                'results': results
            }, f, indent=2)

        # Print summary
        print('\nEvaluation Summary:')
        for result in results:
            print(f'\n{result["model"]} ({result["model_id"]}):')
            for metric, value in result['aggregates'].items():
                print(f'{metric}: {value:.2%}')

        print(f'\nDetailed results saved to {output_file}')

    except Exception as e:
        print(f'Error during evaluation: {str(e)}')

if __name__ == '__main__':
    print('Starting semantic evaluation of fine-tuned models...')
    main()
