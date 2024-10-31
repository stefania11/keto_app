import os
import json
import time
import logging
import asyncio
from typing import List, Dict, Any
import aiohttp
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DeepSeekEvaluator:
    def __init__(self):
        self.api_key = os.getenv('deepseek_api')
        if not self.api_key:
            raise ValueError("DeepSeek API key not found in environment variables")
        logging.info("API key loaded successfully")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        logging.info("SentenceTransformer model loaded")
        self.rate_limit_delay = 1.0  # Delay between requests in seconds
        self.last_request_time = 0

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        try:
            embeddings1 = self.model.encode([text1])
            embeddings2 = self.model.encode([text2])
            similarity = cosine_similarity(embeddings1, embeddings2)[0][0]
            return float(similarity)
        except Exception as e:
            logging.error(f"Error calculating similarity: {str(e)}")
            return 0.0

    async def evaluate_project(self, prompt: str, expected_completion: str, session: aiohttp.ClientSession) -> Dict[str, Any]:
        # Rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last_request)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at analyzing Scratch projects. Describe the given project's structure and components accurately."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                async with session.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    self.last_request_time = time.time()

                    if response.status == 429:  # Rate limit exceeded
                        retry_after = int(response.headers.get('Retry-After', 60))
                        logging.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    response_json = await response.json()

                    completion = response_json["choices"][0]["message"]["content"]
                    exact_match = completion.strip() == expected_completion.strip()
                    semantic_similarity = self.calculate_semantic_similarity(completion, expected_completion)

                    return {
                        "prompt": prompt,
                        "expected": expected_completion,
                        "generated": completion,
                        "exact_match": exact_match,
                        "semantic_similarity": semantic_similarity,
                        "attempt": attempt + 1
                    }

            except asyncio.TimeoutError:
                logging.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                return None

            except Exception as e:
                logging.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                    continue
                return None

        return None

    async def evaluate_dataset(self, test_data: List[Dict[str, str]]) -> Dict[str, Any]:
        results = []
        exact_matches = 0
        total_similarity = 0.0
        checkpoint_file = Path("src/evaluation/results/evaluation_checkpoint.json")

        # Load checkpoint if exists
        start_index = 0
        if checkpoint_file.exists():
            try:
                checkpoint_data = json.loads(checkpoint_file.read_text())
                results = checkpoint_data.get('results', [])
                exact_matches = checkpoint_data.get('exact_matches', 0)
                total_similarity = checkpoint_data.get('total_similarity', 0.0)
                start_index = checkpoint_data.get('next_index', 0)
                logging.info(f"Resuming from checkpoint at index {start_index}")
            except Exception as e:
                logging.error(f"Error loading checkpoint: {str(e)}")

        async with aiohttp.ClientSession() as session:
            for i in range(start_index, len(test_data)):
                logging.info(f"Evaluating item {i+1}/{len(test_data)}")

                result = await self.evaluate_project(
                    test_data[i]["prompt"],
                    test_data[i]["completion"],
                    session
                )

                if result:
                    results.append(result)
                    if result["exact_match"]:
                        exact_matches += 1
                    total_similarity += result["semantic_similarity"]

                    # Save checkpoint every 5 items
                    if (i + 1) % 5 == 0:
                        checkpoint_data = {
                            'results': results,
                            'exact_matches': exact_matches,
                            'total_similarity': total_similarity,
                            'next_index': i + 1
                        }
                        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
                        checkpoint_file.write_text(json.dumps(checkpoint_data))
                        logging.info(f"Checkpoint saved at index {i+1}")

        total_evaluated = len(results)
        if total_evaluated > 0:
            final_results = {
                "model_name": "deepseek-chat",
                "total_evaluated": total_evaluated,
                "exact_match_accuracy": exact_matches / total_evaluated,
                "avg_semantic_similarity": total_similarity / total_evaluated,
                "detailed_results": results,
                "timestamp": int(time.time())
            }

            # Clean up checkpoint file
            if checkpoint_file.exists():
                checkpoint_file.unlink()

            return final_results
        return None

async def main():
    logging.info("Starting DeepSeek evaluation")
    input_file = Path("src/data/medium_complexity_projects.jsonl")

    try:
        logging.info(f"Loading test data from {input_file}")
        test_data = []
        for line in input_file.read_text().splitlines():
            if line.strip():
                try:
                    test_data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logging.error(f"Error parsing JSON line: {e}")
                    continue

        logging.info(f"Loaded {len(test_data)} test cases")

        evaluator = DeepSeekEvaluator()
        logging.info("Initialized DeepSeekEvaluator")
        results = await evaluator.evaluate_dataset(test_data)

        if results:
            output_dir = Path("src/evaluation/results")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"deepseek_evaluation_results_{results['timestamp']}.json"

            output_file.write_text(json.dumps(results, indent=2))

            logging.info("\nEvaluation Results:")
            logging.info(f"Total evaluated: {results['total_evaluated']}")
            logging.info(f"Exact match accuracy: {results['exact_match_accuracy']:.2%}")
            logging.info(f"Average semantic similarity: {results['avg_semantic_similarity']:.2%}")
            logging.info(f"\nDetailed results saved to: {output_file}")
        else:
            logging.error("No results were generated from the evaluation")

    except Exception as e:
        logging.error(f"Fatal error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
