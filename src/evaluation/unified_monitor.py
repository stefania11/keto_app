import json
import time
import logging
from pathlib import Path
from datetime import datetime
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('src/evaluation/logs/unified_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

class UnifiedMonitor:
    def __init__(self):
        self.results_dir = Path('src/evaluation/results')
        self.logs_dir = Path('src/evaluation/logs')
        self.logs_dir.mkdir(exist_ok=True)
        self.start_time = time.time()

    def estimate_completion_time(self, current, total):
        elapsed_time = time.time() - self.start_time
        if current == 0:
            return "Calculating..."
        rate = current / elapsed_time
        remaining_time = (total - current) / rate
        hours = int(remaining_time // 3600)
        minutes = int((remaining_time % 3600) // 60)
        return f"{hours}h {minutes}m"

    def analyze_claude_progress(self):
        claude_files = list(self.results_dir.glob('claude_evaluation_intermediate_*.json'))
        if not claude_files:
            return None

        latest_file = max(claude_files, key=lambda x: x.stat().st_mtime)
        with open(latest_file) as f:
            data = json.load(f)

        total_evaluated = data.get('total_evaluated', 0)
        avg_similarity = data.get('avg_semantic_similarity', 0)
        completion_time = self.estimate_completion_time(total_evaluated, 13256)

        return {
            'total_evaluated': total_evaluated,
            'completion_percentage': (total_evaluated / 13256) * 100,
            'avg_similarity': avg_similarity,
            'estimated_completion': completion_time
        }

    def analyze_gpt2_progress(self):
        log_file = Path('src/fine_tuning/logs/training_detailed.log')
        if not log_file.exists():
            return None

        with open(log_file) as f:
            lines = f.readlines()

        # Extract latest progress and loss
        progress_info = None
        recent_losses = []
        for line in reversed(lines):
            if 'Loss' in line:
                try:
                    loss = float(line.split('Loss = ')[-1].strip())
                    recent_losses.append(loss)
                except ValueError:
                    continue
            if '|' in line and '%' in line:
                progress_info = line.strip()
                break

        if not progress_info:
            return None

        # Parse progress
        try:
            current, total = map(int, progress_info.split('|')[0].strip().split('/'))
            completion_time = self.estimate_completion_time(current, total)
            avg_loss = np.mean(recent_losses[:5]) if recent_losses else 0

            return {
                'current_step': current,
                'total_steps': total,
                'completion_percentage': (current / total) * 100,
                'avg_recent_loss': avg_loss,
                'estimated_completion': completion_time
            }
        except Exception as e:
            logger.error(f"Error parsing GPT-2 progress: {e}")
            return None

    def generate_report(self):
        report = f"""=== Unified Progress Report ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n"""

        # Claude Progress
        claude_progress = self.analyze_claude_progress()
        if claude_progress:
            report += f"""\nClaude Evaluation:
- Progress: {claude_progress['total_evaluated']}/13256 ({claude_progress['completion_percentage']:.1f}%)
- Average Similarity: {claude_progress['avg_similarity']:.4f}
- Estimated Completion: {claude_progress['estimated_completion']}"""

        # DeepSeek Results (Complete)
        report += """\n\nDeepSeek Evaluation:
- Status: Complete (30/30 projects)
- Average Similarity: 0.6156
- Exact Match Accuracy: 0.00%"""

        # GPT-2 Training Progress
        gpt2_progress = self.analyze_gpt2_progress()
        if gpt2_progress:
            report += f"""\n\nGPT-2 Training:
- Progress: {gpt2_progress['current_step']}/{gpt2_progress['total_steps']} ({gpt2_progress['completion_percentage']:.1f}%)
- Average Recent Loss: {gpt2_progress['avg_recent_loss']:.4f}
- Estimated Completion: {gpt2_progress['estimated_completion']}"""

        report += "\n\n=== End Report ===\n"

        # Save report
        report_file = self.results_dir / 'unified_progress.txt'
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(report)
        return report

def main():
    monitor = UnifiedMonitor()
    while True:
        try:
            monitor.generate_report()
            time.sleep(60)  # Update every minute
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
