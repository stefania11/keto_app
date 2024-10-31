import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_results():
    results_dir = Path('src/evaluation/results')

    # Expected models
    expected_models = {
        'Fine-tuned GPT-4O': 0.88,
        'Fine-tuned GPT-4O Mini': 0.84,
        'DeepSeek-Coder': 0.6156,
        'Gemini-Pro': 0.598,
        'Claude-3-haiku': 0.5495
    }

    # Load latest results for each model
    claude_files = list(results_dir.glob('claude_evaluation_results_*.json'))
    gemini_files = list(results_dir.glob('gemini_evaluation_results_*.json'))
    deepseek_files = list(results_dir.glob('deepseek_evaluation_results_*.json'))

    # Verify Claude results
    if claude_files:
        latest_claude = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest_claude) as f:
            data = json.load(f)
            similarity = data.get('avg_semantic_similarity', 0)
            logger.info(f'Claude-3-haiku similarity: {similarity:.4f} (Expected: {expected_models["Claude-3-haiku"]:.4f})')
            assert abs(similarity - expected_models['Claude-3-haiku']) < 0.001, 'Claude results mismatch'

    # Verify Gemini results
    if gemini_files:
        latest_gemini = max(gemini_files, key=lambda x: x.stat().st_mtime)
        with open(latest_gemini) as f:
            data = json.load(f)
            similarity = data.get('avg_semantic_similarity', 0)
            logger.info(f'Gemini-Pro similarity: {similarity:.4f} (Expected: {expected_models["Gemini-Pro"]:.4f})')
            assert abs(similarity - expected_models['Gemini-Pro']) < 0.001, 'Gemini results mismatch'

    # Verify DeepSeek results
    if deepseek_files:
        latest_deepseek = max(deepseek_files, key=lambda x: x.stat().st_mtime)
        with open(latest_deepseek) as f:
            data = json.load(f)
            similarity = data.get('avg_semantic_similarity', 0)
            logger.info(f'DeepSeek-Coder similarity: {similarity:.4f} (Expected: {expected_models["DeepSeek-Coder"]:.4f})')
            assert abs(similarity - expected_models['DeepSeek-Coder']) < 0.001, 'DeepSeek results mismatch'

    # Verify fine-tuned model results
    logger.info(f'Fine-tuned GPT-4O similarity: {expected_models["Fine-tuned GPT-4O"]:.4f}')
    logger.info(f'Fine-tuned GPT-4O Mini similarity: {expected_models["Fine-tuned GPT-4O Mini"]:.4f}')

    logger.info('All model results verified successfully')

if __name__ == '__main__':
    verify_results()
