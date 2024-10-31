import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_current_evaluations() -> Dict[str, float]:
    results_dir = Path('src/evaluation/results')
    current_models = {}

    # Load Claude results
    claude_files = list(results_dir.glob('claude_evaluation_results_*.json'))
    if claude_files:
        latest_claude = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest_claude) as f:
            data = json.load(f)
            current_models['Claude-3-haiku'] = data.get('avg_semantic_similarity', 0)

    # Load Gemini results
    gemini_files = list(results_dir.glob('gemini_evaluation_results_*.json'))
    if gemini_files:
        latest_gemini = max(gemini_files, key=lambda x: x.stat().st_mtime)
        with open(latest_gemini) as f:
            data = json.load(f)
            current_models['Gemini-Pro'] = data.get('avg_semantic_similarity', 0)

    # Load DeepSeek results
    deepseek_files = list(results_dir.glob('deepseek_evaluation_results_*.json'))
    if deepseek_files:
        latest_deepseek = max(deepseek_files, key=lambda x: x.stat().st_mtime)
        with open(latest_deepseek) as f:
            data = json.load(f)
            current_models['DeepSeek-Coder'] = data.get('avg_semantic_similarity', 0)

    return current_models

def get_previous_models() -> Dict[str, float]:
    return {
        'Fine-tuned GPT-4O': 0.88,
        'Fine-tuned GPT-4O Mini': 0.84
    }

def generate_comparison_table() -> str:
    current_models = load_current_evaluations()
    previous_models = get_previous_models()

    # Combine all models
    all_models = {**current_models, **previous_models}

    # Sort by performance
    sorted_models = sorted(all_models.items(), key=lambda x: x[1], reverse=True)

    # Generate markdown table
    table = "| Model | Semantic Similarity | Type |\n"
    table += "|:------|:-------------------|:------|\n"

    for model, similarity in sorted_models:
        model_type = "Fine-tuned" if "Fine-tuned" in model else "Base"
        table += f"| {model} | {similarity:.4f} | {model_type} |\n"

    return table

def save_comparison(table: str):
    output_file = Path('src/evaluation/results/model_comparison.md')
    with open(output_file, 'w') as f:
        f.write("# Model Comparison Results\n\n")
        f.write("Comparison of all evaluated models on the same set of 30 medium-complexity projects:\n\n")
        f.write(table)
        f.write("\n\nNotes:\n")
        f.write("- All evaluations performed on the same set of 30 medium-complexity projects\n")
        f.write("- Semantic similarity calculated using SentenceTransformer (all-MiniLM-L6-v2)\n")
        f.write("- Base models use temperature=0.2 for consistent output format\n")

def main():
    logger.info("Generating comprehensive model comparison")
    table = generate_comparison_table()
    save_comparison(table)
    logger.info("Comparison table saved to src/evaluation/results/model_comparison.md")
    print("\nModel Comparison Table:")
    print(table)

if __name__ == "__main__":
    main()
