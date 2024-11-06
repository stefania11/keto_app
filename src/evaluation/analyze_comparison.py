import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_latest_results(results_dir: Path, pattern: str) -> dict:
    """Load the latest results file matching the given pattern."""
    files = list(results_dir.glob(pattern))
    if not files:
        return None

    latest_file = max(files, key=lambda x: x.stat().st_mtime)
    with open(latest_file) as f:
        return json.load(f)

def create_comparison_table():
    results_dir = Path('src/evaluation/results')

    # Load latest results for each model
    claude_results = load_latest_results(results_dir, 'claude_evaluation_results_*.json')
    gemini_results = load_latest_results(results_dir, 'gemini_evaluation_results_*.json')
    deepseek_results = load_latest_results(results_dir, 'deepseek_evaluation_results_*.json')

    # Prepare comparison data
    comparison_data = {
        'Model': [],
        'Projects Evaluated': [],
        'Average Semantic Similarity': [],
        'Status': []
    }

    # Add Claude results
    if claude_results:
        comparison_data['Model'].append('Claude-3-haiku')
        comparison_data['Projects Evaluated'].append(f"{claude_results.get('total_evaluated', 0)}/30")
        comparison_data['Average Semantic Similarity'].append(
            claude_results.get('avg_semantic_similarity', 0)
        )
        comparison_data['Status'].append(
            'Complete' if claude_results.get('total_evaluated', 0) >= 30 else 'In Progress'
        )

    # Add Gemini results
    if gemini_results:
        comparison_data['Model'].append('Gemini-Pro')
        comparison_data['Projects Evaluated'].append(f"{gemini_results.get('total_evaluated', 0)}/30")
        comparison_data['Average Semantic Similarity'].append(
            gemini_results.get('avg_semantic_similarity', 0)
        )
        comparison_data['Status'].append(
            'Complete' if gemini_results.get('total_evaluated', 0) >= 30 else 'In Progress'
        )

    # Add DeepSeek results
    if deepseek_results:
        comparison_data['Model'].append('DeepSeek-Coder')
        comparison_data['Projects Evaluated'].append(f"{len(deepseek_results.get('results', []))}/30")
        comparison_data['Average Semantic Similarity'].append(
            deepseek_results.get('avg_semantic_similarity', 0)
        )
        comparison_data['Status'].append(
            'Complete' if len(deepseek_results.get('results', [])) >= 30 else 'In Progress'
        )

    # Create DataFrame and format it
    df = pd.DataFrame(comparison_data)
    df['Average Semantic Similarity'] = df['Average Semantic Similarity'].apply(
        lambda x: f"{x:.4f}"
    )

    # Generate markdown table
    markdown_table = f"""# Model Evaluation Comparison
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{df.to_markdown(index=False)}

## Notes:
- All evaluations performed on the same set of 30 medium-complexity projects
- Semantic similarity calculated using SentenceTransformer (all-MiniLM-L6-v2)
- All models configured with temperature=0.2 for consistent output format
"""

    # Save comparison to file
    output_file = results_dir / 'model_comparison.md'
    with open(output_file, 'w') as f:
        f.write(markdown_table)

    logger.info(f"Comparison table saved to {output_file}")
    return markdown_table

if __name__ == '__main__':
    comparison = create_comparison_table()
    print(comparison)
