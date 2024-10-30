import os
import json
import pandas as pd
from openai import OpenAI
from anthropic import Anthropic
import requests
from pathlib import Path
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch
import backoff
import time
import traceback
import argparse

def load_evaluation_data(file_path):
    """Load evaluation dataset from CSV file and convert to required format."""
    df = pd.read_csv(file_path)
    evaluation_data = []
    for _, row in df.iterrows():
        evaluation_data.append({
            "prompt": f"Describe Scratch project ID {row['project_id']}",
            "completion": f" blocks:\nsprite: Project_{row['project_id']}"
        })
    return evaluation_data

def calculate_semantic_similarity(str1, str2):
    """Calculate semantic similarity between two strings using sentence transformers."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([str1, str2])
    return util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()

@backoff.on_exception(backoff.expo,
                     Exception,
                     max_tries=5,
                     max_time=300)
def make_openai_call(client, model_name, messages):
    """Make OpenAI API call with retry logic."""
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        raise

@backoff.on_exception(backoff.expo,
                     Exception,
                     max_tries=5,
                     max_time=300)
def make_anthropic_call(client, model_name, prompt):
    """Make Anthropic API call with retry logic."""
    try:
        message = client.messages.create(
            model=model_name,
            max_tokens=150,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return message.content[0].text.strip()
    except Exception as e:
        print(f"Error in Anthropic API call: {str(e)}")
        raise

@backoff.on_exception(backoff.expo,
                     Exception,
                     max_tries=5,
                     max_time=300)
def make_deepseek_call(api_key, prompt):
    """Make DeepSeek API call with retry logic."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-coder-v2",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error in DeepSeek API call: {str(e)}")
        raise

def evaluate_model(model_provider, client, model_name, evaluation_data, api_key=None):
    """Evaluate a model's performance on the test data."""
    results = []
    format_accuracy = 0
    sprite_accuracy = 0
    semantic_similarity_sum = 0
    total_examples = len(evaluation_data)

    for example in tqdm(evaluation_data, desc=f"Evaluating {model_name}"):
        prompt = example['prompt']
        expected_completion = example['completion']

        try:
            if model_provider == "openai":
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that describes Scratch projects."},
                    {"role": "user", "content": prompt}
                ]
                model_completion = make_openai_call(client, model_name, messages)
            elif model_provider == "anthropic":
                system_prompt = "You are a helpful assistant that describes Scratch projects."
                full_prompt = f"{system_prompt}\n\n{prompt}"
                model_completion = make_anthropic_call(client, model_name, full_prompt)
            elif model_provider == "deepseek":
                system_prompt = "You are a helpful assistant that describes Scratch projects."
                full_prompt = f"{system_prompt}\n\n{prompt}"
                model_completion = make_deepseek_call(api_key, full_prompt)
            else:
                raise ValueError(f"Unsupported model provider: {model_provider}")

            # Format accuracy
            if model_completion.startswith(" blocks:") and "sprite:" in model_completion:
                format_accuracy += 1

            # Sprite accuracy
            expected_sprite = expected_completion.split("sprite: ")[1].strip()
            if expected_sprite in model_completion:
                sprite_accuracy += 1

            # Semantic similarity
            semantic_similarity = calculate_semantic_similarity(expected_completion, model_completion)
            semantic_similarity_sum += semantic_similarity

            results.append({
                "prompt": prompt,
                "expected": expected_completion,
                "generated": model_completion,
                "semantic_similarity": semantic_similarity
            })

            # Add a small delay to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Error processing example {prompt}: {str(e)}")
            traceback.print_exc()
            continue

    metrics = {
        "format_accuracy": (format_accuracy / total_examples) * 100,
        "sprite_accuracy": (sprite_accuracy / total_examples) * 100,
        "semantic_similarity": semantic_similarity_sum / total_examples
    }

    return metrics, results

def save_results(metrics, results, model_name, output_dir):
    """Save evaluation results to files."""
    os.makedirs(output_dir, exist_ok=True)

    # Save detailed results
    results_file = os.path.join(output_dir, f"evaluation_results_{model_name.replace(':', '_')}.json")
    with open(results_file, 'w') as f:
        json.dump({
            "metrics": metrics,
            "results": results
        }, f, indent=2)

    print(f"\nResults for {model_name}:")
    print(f"Format Accuracy: {metrics['format_accuracy']:.2f}%")
    print(f"Sprite Accuracy: {metrics['sprite_accuracy']:.2f}%")
    print(f"Semantic Similarity: {metrics['semantic_similarity']:.4f}")

def main():
    """Run evaluation on all specified models."""
    # Create results directory
    output_dir = Path(__file__).parent / "results"
    os.makedirs(output_dir, exist_ok=True)

    # Initialize clients with environment variables
    openai_client = OpenAI(
        api_key=os.environ["OAI_key"],
        organization=os.environ["OAI_organization_id"]
    )
    anthropic_client = Anthropic(api_key=os.environ.get("anthropic_api"))
    deepseek_api_key = os.environ.get("deepseek_api")

    # Load evaluation data
    evaluation_data_path = Path(__file__).parent.parent / "data" / "medium_complexity_projects.csv"
    evaluation_data = load_evaluation_data(evaluation_data_path)

    # Define models to evaluate
    models_to_evaluate = [
        {"provider": "openai", "name": "gpt-4-0613"},
        {"provider": "openai", "name": "ft:gpt-4-0613:personal::8K2glPZx"},
        {"provider": "anthropic", "name": "claude-3-sonnet-20240229"},
        {"provider": "deepseek", "name": "deepseek-coder-v2"}
    ]

    output_dir = Path(__file__).parent / "results"
    os.makedirs(output_dir, exist_ok=True)

    all_metrics = []
    for model in models_to_evaluate:
        provider = model["provider"]
        model_name = model["name"]

        print(f"\nEvaluating {provider} model: {model_name}")

        if provider == "openai":
            metrics, results = evaluate_model(provider, openai_client, model_name, evaluation_data)
        elif provider == "anthropic":
            metrics, results = evaluate_model(provider, anthropic_client, model_name, evaluation_data)
        elif provider == "deepseek":
            metrics, results = evaluate_model(provider, None, model_name, evaluation_data, api_key=deepseek_api_key)

        save_results(metrics, results, model_name, output_dir)

        all_metrics.append({
            "model": model_name,
            "provider": provider,
            **metrics
        })

    # Save comparison table
    comparison_df = pd.DataFrame(all_metrics)
    comparison_file = output_dir / "model_comparison.csv"
    comparison_df.to_csv(comparison_file, index=False)
    print(f"\nModel comparison saved to {comparison_file}")

if __name__ == "__main__":
    main()
