import logging
from sentence_transformers import SentenceTransformer
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_similarity_calculation():
    # Initialize the model
    logger.info("Loading similarity model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Test with sample texts
    text1 = """blocks:
sprite: Sprite1
  event_whenflagclicked: []
  motion_movensteps: [10]
  control_repeat: [10]"""

    text2 = """blocks:
sprite: Sprite1
  event_whenflagclicked: []
  motion_movensteps: [10]
  control_repeat: [8]"""

    # Calculate embeddings and similarity
    logger.info("Calculating similarity for test cases...")
    embeddings1 = model.encode([text1])
    embeddings2 = model.encode([text2])
    similarity = float(embeddings1 @ embeddings2.T)

    logger.info(f"Test similarity score: {similarity:.4f}")

    # Test with actual results
    results_dir = Path('src/evaluation/results')
    claude_files = list(results_dir.glob('claude_evaluation_intermediate_*.json'))

    if claude_files:
        latest_file = max(claude_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"\nTesting with actual results from {latest_file}")

        with open(latest_file) as f:
            data = json.load(f)
            results = data.get('results', [])

            if len(results) >= 2:
                # Test similarity calculation with last two results
                response1 = results[-2].get('response', '')
                response2 = results[-1].get('response', '')

                embeddings1 = model.encode([response1])
                embeddings2 = model.encode([response2])
                similarity = float(embeddings1 @ embeddings2.T)

                logger.info("Sample from actual results:")
                logger.info(f"Response 1:\n{response1[:200]}...")
                logger.info(f"Response 2:\n{response2[:200]}...")
                logger.info(f"Calculated similarity: {similarity:.4f}")

if __name__ == '__main__':
    test_similarity_calculation()
