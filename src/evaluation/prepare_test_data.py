import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def prepare_test_data():
    # Create data directory if it doesn't exist
    data_dir = Path('src/data')
    data_dir.mkdir(exist_ok=True)

    # Load existing evaluation results
    results_dir = Path('src/evaluation/results')
    claude_files = list(results_dir.glob('claude_evaluation_*.json'))

    if not claude_files:
        logger.error("No Claude evaluation results found to prepare test data")
        return

    # Get the latest Claude results file
    latest_claude = max(claude_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"Using {latest_claude} for test data preparation")

    test_cases = []
    with open(latest_claude, 'r') as f:
        data = json.load(f)
        results = data.get('results', [])

        for result in results:
            if 'project_id' in result and 'response' in result:
                test_case = {
                    'prompt': f"Analyze Scratch project {result['project_id']}",
                    'completion': result['response']
                }
                test_cases.append(test_case)

    # Take a subset of 30 test cases
    test_cases = test_cases[:30]
    logger.info(f"Prepared {len(test_cases)} test cases")

    # Save test data in JSONL format
    output_file = data_dir / 'test_data.jsonl'
    with open(output_file, 'w') as f:
        for case in test_cases:
            f.write(json.dumps(case) + '\n')

    logger.info(f"Test data saved to {output_file}")

if __name__ == '__main__':
    prepare_test_data()
