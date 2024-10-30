import os
import json
import pandas as pd
from openai import OpenAI
from pathlib import Path
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
import torch

# Initialize OpenAI client with API key and organization
client = OpenAI(
    api_key=os.environ.get('OAI_key'),
    organization=os.environ.get('OAI_organization_id')
)

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

def evaluate_model(model_name, evaluation_data, output_file):
    """Evaluate a model on the test data."""
    results = []

    print(f"\nEvaluating model: {model_name}")
    for item in tqdm(evaluation_data):
        try:
            # Get model completion
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You analyze Scratch projects and describe their structure."},
                    {"role": "user", "content": item["prompt"]}
                ],
                temperature=0.7,
                max_tokens=150
            )

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

        except Exception as e:
            print(f"Error evaluating prompt: {item['prompt']}")
            print(f"Error: {str(e)}")
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

def main():
    """Run evaluation on all specified models."""
    # Create results directory
    os.makedirs("src/evaluation/results", exist_ok=True)

    # Load evaluation data
    print("Loading evaluation data...")
    evaluation_data = load_evaluation_data()

    # Models to evaluate
    models = [
        "gpt-4-0613",  # Base model for comparison
        "ft:gpt-4-0613:personal::8K2glPZx",  # Replace with your actual fine-tuned model ID
    ]

    # Run evaluation for each model
    all_metrics = []
    for model in models:
        metrics = evaluate_model(
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
    main()
