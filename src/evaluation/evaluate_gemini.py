import os
import json
import time
import logging
import google.generativeai as genai
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/gemini_evaluation.log')
    ]
)
logger = logging.getLogger(__name__)

class GeminiEvaluator:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY') or os.getenv('gemini_api')
        if not self.api_key:
            raise ValueError("Gemini API key not found")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.similarity_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Initialized Gemini evaluator with similarity model")

    def evaluate_project(self, project_data: Dict[str, Any], max_retries=3) -> Dict[str, Any]:
        prompt = f"""### Instruction: Analyze the following Scratch project and describe its structure using block format.
### Input: {project_data['prompt']}
### Response: Please provide the project structure in block format, listing sprites and their blocks."""

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=1000,
                    )
                )
                generated_text = response.text.strip()

                return {
                    "prompt": project_data['prompt'],
                    "generated": generated_text,
                    "expected": project_data['completion'],
                    "timestamp": time.time()
                }
            except Exception as e:
                wait_time = (attempt + 1) * 5
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("All attempts failed")
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
            return float(max(0.0, min(1.0, similarity)))
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
    output_file = f"src/evaluation/results/gemini_evaluation_results_{timestamp}.json"

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
    logger.info("Starting Gemini evaluation with 30 test cases")

    try:
        test_data = load_test_data('src/data/test_data.jsonl')
        if not test_data:
            raise ValueError("No test data loaded")

        test_data = test_data[:30]
        logger.info(f"Using {len(test_data)} test cases")

        evaluator = GeminiEvaluator()
        results = []

        for i, test_case in enumerate(test_data, 1):
            logger.info(f"Evaluating test case {i}/{len(test_data)}")
            result = evaluator.evaluate_project(test_case)

            if result:
                similarity = evaluator.calculate_similarity(
                    result['generated'],
                    result['expected']
                )
                result['semantic_similarity'] = similarity
                logger.info(f"Calculated similarity: {similarity:.4f}")

                results.append(result)

                if len(results) % 10 == 0:
                    save_results(results, len(results))

            time.sleep(2)

        save_results(results, len(results))

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        if results:
            save_results(results, len(results))
        raise

if __name__ == "__main__":
    main()
