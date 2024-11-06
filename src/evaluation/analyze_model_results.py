import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_results():
    """Analyze and compare results from all models."""
    results_dir = Path('src/evaluation/results')
    
    # Analyze DeepSeek results
    deepseek_files = list(results_dir.glob('deepseek_evaluation_*.json'))
    if deepseek_files:
        latest = max(deepseek_files, key=lambda x: x.stat().st_mtime)
        with open(latest) as f:
            data = json.load(f)
            results = data.get('detailed_results', [])
            if results:
                logger.info("\nDeepSeek Results:")
                logger.info(f"Total evaluated: {len(results)}/30")
                exact_matches = sum(1 for r in results if r.get('exact_match', False))
                logger.info(f"Exact match accuracy: {exact_matches/len(results):.2%}")
                avg_sim = sum(r.get('semantic_similarity', 0) for r in results) / len(results)
                logger.info(f"Average semantic similarity: {avg_sim:.3f}")
    
    # Analyze Claude results
    claude_files = list(results_dir.glob('claude_evaluation_*.json'))
    if claude_files:
        latest = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest) as f:
            data = json.load(f)
            logger.info("\nClaude Results:")
            total = data.get('total_evaluated', 0)
            logger.info(f"Progress: {total}/13256 ({total/13256:.1%})")
            if 'exact_match_accuracy' in data:
                logger.info(f"Exact match accuracy: {data['exact_match_accuracy']:.2%}")
            if 'avg_semantic_similarity' in data:
                logger.info(f"Average semantic similarity: {data['avg_semantic_similarity']:.3f}")
    
    # Check GPT-2 training progress
    training_log = Path('src/fine_tuning/logs/training_detailed.log')
    if training_log.exists():
        with open(training_log) as f:
            lines = f.readlines()
            if lines:
                for line in reversed(lines):
                    if 'Loss' in line:
                        logger.info("\nGPT-2 Training:")
                        logger.info(f"Latest status: {line.strip()}")
                        break

if __name__ == '__main__':
    analyze_results()
