import json
import time
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/evaluation_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

def check_evaluation_progress():
    results_dir = Path('src/evaluation/results')

    # Check Claude results
    claude_files = list(results_dir.glob('claude_evaluation_results_*.json'))
    if claude_files:
        latest_claude = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest_claude) as f:
            claude_data = json.load(f)
            logger.info("\nClaude Evaluation Status:")
            logger.info(f"Total evaluated: {claude_data.get('total_evaluated', 0)}/30")
            logger.info(f"Average similarity: {claude_data.get('avg_semantic_similarity', 0):.4f}")

    # Check Gemini results
    gemini_files = list(results_dir.glob('gemini_evaluation_results_*.json'))
    if gemini_files:
        latest_gemini = max(gemini_files, key=lambda x: x.stat().st_mtime)
        with open(latest_gemini) as f:
            gemini_data = json.load(f)
            logger.info("\nGemini Evaluation Status:")
            logger.info(f"Total evaluated: {gemini_data.get('total_evaluated', 0)}/30")
            logger.info(f"Average similarity: {gemini_data.get('avg_semantic_similarity', 0):.4f}")

def main():
    logger.info("Starting evaluation monitoring")
    while True:
        try:
            check_evaluation_progress()
            time.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            time.sleep(30)

if __name__ == '__main__':
    main()
