import json
import time
import logging
from pathlib import Path
from datetime import datetime
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('src/evaluation/logs/analysis.log')
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveAnalyzer:
    def __init__(self):
        self.results_dir = Path('src/evaluation/results')
        self.logs_dir = Path('src/evaluation/logs')
        self.logs_dir.mkdir(exist_ok=True)

    def analyze_claude_results(self):
        claude_files = list(self.results_dir.glob('claude_evaluation_intermediate_*.json'))
        if not claude_files:
            return None

        latest_file = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file) as f:
            data = json.load(f)

        total_evaluated = data.get('total_evaluated', 0)
        avg_similarity = data.get('avg_semantic_similarity', 0)

        # Analyze last 5 results for detailed inspection
        results = data.get('results', [])[-5:]
        recent_similarities = [r.get('semantic_similarity', 0) for r in results]

        return {
            'total_evaluated': total_evaluated,
            'avg_similarity': avg_similarity,
            'recent_similarities': recent_similarities,
            'completion_percentage': (total_evaluated / 13256) * 100
        }

    def analyze_deepseek_results(self):
        deepseek_files = list(self.results_dir.glob('deepseek_evaluation_results_*.json'))
        if not deepseek_files:
            return None

        latest_file = max(deepseek_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file) as f:
            data = json.load(f)

        total_evaluated = len(data.get('results', []))
        exact_match_accuracy = data.get('exact_match_accuracy', 0)
        avg_similarity = data.get('avg_semantic_similarity', 0)

        return {
            'total_evaluated': total_evaluated,
            'exact_match_accuracy': exact_match_accuracy,
            'avg_similarity': avg_similarity,
            'completion_percentage': (total_evaluated / 30) * 100
        }

    def analyze_gpt2_training(self):
        log_file = Path('src/fine_tuning/logs/training_detailed.log')
        if not log_file.exists():
            return None

        with open(log_file) as f:
            lines = f.readlines()

        # Extract training progress and loss values
        progress_line = None
        loss_values = []
        for line in reversed(lines):
            if 'Loss' in line:
                try:
                    loss = float(line.split('Loss = ')[-1].strip())
                    loss_values.append(loss)
                except ValueError:
                    continue
            if '|' in line and '%' in line:
                progress_line = line
                break

        if not progress_line:
            return None

        # Parse progress information using regex
        match = re.search(r'(\d+)/(\d+)', progress_line)
        if not match:
            return None

        current_step = int(match.group(1))
        total_steps = int(match.group(2))

        return {
            'current_step': current_step,
            'total_steps': total_steps,
            'completion_percentage': (current_step / total_steps) * 100,
            'recent_losses': loss_values[:5]
        }

    def generate_report(self):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report = f"""
=== Comprehensive Analysis Report ({timestamp}) ===

1. Claude Evaluation:
"""
        claude_results = self.analyze_claude_results()
        if claude_results:
            report += f"""   - Progress: {claude_results['total_evaluated']}/13256 ({claude_results['completion_percentage']:.1f}%)
   - Average Similarity: {claude_results['avg_similarity']:.4f}
   - Recent Similarities: {', '.join(f'{x:.4f}' for x in claude_results['recent_similarities'])}
"""

        report += "\n2. DeepSeek Evaluation:"
        deepseek_results = self.analyze_deepseek_results()
        if deepseek_results:
            report += f"""   - Progress: {deepseek_results['total_evaluated']}/30 ({deepseek_results['completion_percentage']:.1f}%)
   - Exact Match Accuracy: {deepseek_results['exact_match_accuracy']:.2%}
   - Average Similarity: {deepseek_results['avg_similarity']:.4f}
"""

        report += "\n3. GPT-2 Training:"
        gpt2_results = self.analyze_gpt2_training()
        if gpt2_results:
            report += f"""   - Progress: {gpt2_results['current_step']}/{gpt2_results['total_steps']} ({gpt2_results['completion_percentage']:.1f}%)
   - Recent Loss Values: {', '.join(f'{x:.4f}' for x in gpt2_results['recent_losses'])}
"""

        report += "\n=== End Report ==="

        # Save report
        report_file = self.results_dir / 'latest_analysis.txt'
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(report)
        return report

def main():
    analyzer = ComprehensiveAnalyzer()
    while True:
        try:
            analyzer.generate_report()
            time.sleep(60)  # Update every minute
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
