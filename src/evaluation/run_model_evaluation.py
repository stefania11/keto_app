import os
import json
import pandas as pd
from openai import OpenAI
from pathlib import Path
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch
import backoff
import time
import traceback
import argparse

def load_evaluation_data():
    """Load the evaluation dataset."""
    data = []
    with open("src/data/evaluation_data.jsonl", "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data

def calculate_semantic_similarity(pred, target):
    """Calculate semantic similarity between prediction and target."""
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Encode texts to get their embeddings
    embedding1 = model.encode(pred, convert_to_tensor=True)
    embedding2 = model.encode(target, convert_to_tensor=True)

    # Calculate cosine similarity
    similarity = util.pytorch_cos_sim(embedding1, embedding2)
    return float(similarity[0][0])

@backoff.on_exception(backoff.expo,
                     (Exception),
                     max_tries=5,
                     max_time=300)
def make_api_call(client, model_name, messages):
    """Make API call with exponential backoff retry."""
    try:
        return client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
    except Exception as e:
        print(f"API call error for model {model_name}: {str(e)}")
        raise

def evaluate_model(client, model_name, evaluation_data, output_file):
    """Evaluate a model on the test data."""
    results = []

    print(f"\nEvaluating model: {model_name}")
    for item in tqdm(evaluation_data):
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": "You analyze Scratch projects and describe their structure."},
                {"role": "user", "content": item["prompt"]}
            ]

            # Get model completion with retry logic
            response = make_api_call(client, model_name, messages)
            prediction = response.choices[0].message.content

            # Calculate metrics
            exact_match = prediction.strip() == item["completion"].strip()
            semantic_sim = calculate_semantic_similarity(prediction, item["completion"])

            results.append({
                "prompt": item["prompt"],
                "target": item["completion"],
                "prediction": prediction,
                "exact_match": exact_match,
                "semantic_similarity": semantic_sim
            })

            # Add a small delay between requests to avoid rate limiting
            time.sleep(1)

        except Exception as e:
            print(f"Error evaluating prompt: {item['prompt']}")
            print(f"Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            continue

    # Calculate overall metrics
    metrics = {
        "model_name": model_name,
        "total_evaluated": len(results),
        "exact_match_accuracy": np.mean([r["exact_match"] for r in results]),
        "avg_semantic_similarity": np.mean([r["semantic_similarity"] for r in results])
    }

    # Save detailed results
    output_path = f"src/evaluation/results/{output_file}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({
            "metrics": metrics,
            "detailed_results": results
        }, f, indent=2)

    print(f"\nResults saved to {output_path}")
    print("\nMetrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    return metrics

def main(api_key, org_id):
    """Run evaluation on all specified models."""
    # Initialize OpenAI client with provided credentials
    client = OpenAI(
        api_key=api_key.strip(),  # Ensure no whitespace in API key
        organization=org_id.strip()  # Ensure no whitespace in org ID
    )

    # Create results directory
    os.makedirs("src/evaluation/results", exist_ok=True)

    # Load evaluation data
    print("Loading evaluation data...")
    evaluation_data = load_evaluation_data()

    # List of models to evaluate
    models_to_evaluate = [
        "ft:gpt-4o-2024-08-06:personal::AEk9dgyk",  # Latest gpt-4o model
        "ft:gpt-4o-mini-2024-07-18:personal::AEREcDGY",  # Latest gpt-4o-mini model
        "ft:gpt-4o-2024-08-06:personal::AEk9daX3:ckpt-step-1956",  # Checkpoint model for comparison
        "ft:gpt-4o-mini-2024-07-18:personal::AEREcs2S:ckpt-step-1956"  # Checkpoint model for comparison
    ]

    # Run evaluation for each model
    all_metrics = []
    for model in models_to_evaluate:
        metrics = evaluate_model(
            client,
            model,
            evaluation_data,
            f"evaluation_results_{model.replace(':', '_')}.json"
        )
        all_metrics.append(metrics)

    # Save comparison results
    comparison_df = pd.DataFrame(all_metrics)
    comparison_df.to_csv("src/evaluation/results/model_comparison.csv", index=False)
    print("\nModel comparison saved to src/evaluation/results/model_comparison.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate OpenAI models on Scratch project descriptions.")
    parser.add_argument("--api_key", required=True, help="OpenAI API Key")
    parser.add_argument("--org_id", required=True, help="OpenAI Organization ID")
    args = parser.parse_args()

    main(args.api_key, args.org_id)
