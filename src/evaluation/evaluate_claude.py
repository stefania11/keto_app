import os
import json
import time
import logging
import anthropic
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClaudeEvaluator:
    def __init__(self):
        self.api_key = os.getenv('anthropic_api')
        if not self.api_key:
            raise ValueError("Anthropic API key not found")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Initialized Claude evaluator with similarity model")

    def evaluate_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""### Instruction: Analyze the following Scratch project and describe its structure using block format.
### Input: {project_data['prompt']}
### Response: Please provide the project structure in block format, listing sprites and their blocks."""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            generated_text = response.content[0].text.strip()

            return {
                "prompt": project_data['prompt'],
                "generated": generated_text,
                "expected": project_data['completion'],
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"Error evaluating project: {e}")
            return None

    def calculate_similarity(self, text1: str, text2: str) -> float:
        try:
            if not text1.strip() or not text2.strip():
                return 0.0

            embedding1 = self.similarity_model.encode(text1, convert_to_tensor=True)
            embedding2 = self.similarity_model.encode(text2, convert_to_tensor=True)

            embedding1 = embedding1.cpu().numpy()
            embedding2 = embedding2.cpu().numpy()

            embedding1 = embedding1 / np.linalg.norm(embedding1)
            embedding2 = embedding2 / np.linalg.norm(embedding2)

            similarity = np.dot(embedding1, embedding2)
            similarity = float(max(0.0, min(1.0, similarity)))

            return similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

def load_test_data(file_path: str) -> List[Dict[str, Any]]:
    logger.info("Loading test data...")
    test_cases = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                test_cases.append(json.loads(line))
        logger.info(f"Loaded {len(test_cases)} test cases")
        return test_cases
    except Exception as e:
        logger.error(f"Error loading test data: {e}")
        return []

def save_results(results: List[Dict[str, Any]], total_evaluated: int):
    timestamp = int(time.time())
    output_file = f"src/evaluation/results/claude_evaluation_results_{timestamp}.json"

    similarities = [result.get("semantic_similarity", 0.0) for result in results if "semantic_similarity" in result]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

    output_data = {
        "results": results,
        "total_evaluated": total_evaluated,
        "avg_semantic_similarity": avg_similarity,
        "timestamp": timestamp
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    logger.info(f"Saved results to {output_file}")
    logger.info(f"Total evaluated: {total_evaluated}")
    logger.info(f"Average semantic similarity: {avg_similarity:.4f}")

def main():
    logger.info("Starting Claude evaluation with 30 test cases")

    try:
        # Load test data
        test_data = load_test_data('src/data/test_data.jsonl')
        if not test_data:
            raise ValueError("No test data loaded")

        # Limit to 30 projects
        test_data = test_data[:30]
        logger.info(f"Using {len(test_data)} test cases")

        evaluator = ClaudeEvaluator()
        results = []

        # Process test cases
        for i, test_case in enumerate(test_data, 1):
            logger.info(f"Evaluating test case {i}/{len(test_data)}")
            result = evaluator.evaluate_project(test_case)

            if result:
                # Calculate semantic similarity
                similarity = evaluator.calculate_similarity(
                    result['generated'],
                    result['expected']
                )
                result['semantic_similarity'] = similarity
                logger.info(f"Calculated similarity: {similarity:.4f}")

                results.append(result)

                # Save intermediate results every 10 projects
                if len(results) % 10 == 0:
                    save_results(results, len(results))

            # Add delay to avoid rate limiting
            time.sleep(2)

        # Save final results
        save_results(results, len(results))

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        if results:
            save_results(results, len(results))
        raise

if __name__ == "__main__":
    main()
