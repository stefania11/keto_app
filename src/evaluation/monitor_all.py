import json
import time
import logging
from pathlib import Path
from datetime import datetime
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('src/evaluation/logs/monitor.log'),
        logging.StreamHandler()
    ]
)

class ModelMonitor:
    def __init__(self):
        self.results_dir = Path('src/evaluation/results')
        self.training_log = Path('src/fine_tuning/logs/training_detailed.log')
        self.deepseek_log = Path('src/evaluation/logs/deepseek_evaluation.log')
        self.claude_log = Path('src/evaluation/logs/claude_evaluation.log')
        self.last_update = {}

    def read_latest_metrics(self, file_path):
        try:
            if not file_path.exists():
                return None
            with open(file_path, 'r') as f:
                lines = f.readlines()
                return lines[-20:] if lines else []
        except Exception as e:
            logging.error(f"Error reading {file_path}: {str(e)}")
            return None

    def get_latest_results(self):
        results = {}

        # Check GPT-2 training progress
        training_logs = self.read_latest_metrics(self.training_log)
        if training_logs:
            results['gpt2_training'] = {
                'status': 'running',
                'latest_logs': training_logs[-5:]
            }

        # Check DeepSeek evaluation
        deepseek_logs = self.read_latest_metrics(self.deepseek_log)
        if deepseek_logs:
            results['deepseek_evaluation'] = {
                'status': 'running',
                'latest_logs': deepseek_logs[-5:]
            }

        # Check Claude evaluation
        claude_logs = self.read_latest_metrics(self.claude_log)
        if claude_logs:
            results['claude_evaluation'] = {
                'status': 'running',
                'latest_logs': claude_logs[-5:]
            }

        return results

    def format_status_report(self, results):
        report = "\n=== Model Training & Evaluation Status ===\n"
        report += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        if 'gpt2_training' in results:
            report += "GPT-2 Training:\n"
            for log in results['gpt2_training']['latest_logs']:
                report += f"{log.strip()}\n"
            report += "\n"

        if 'deepseek_evaluation' in results:
            report += "DeepSeek Evaluation:\n"
            for log in results['deepseek_evaluation']['latest_logs']:
                report += f"{log.strip()}\n"
            report += "\n"

        if 'claude_evaluation' in results:
            report += "Claude Evaluation:\n"
            for log in results['claude_evaluation']['latest_logs']:
                report += f"{log.strip()}\n"
            report += "\n"

        return report

    def monitor(self):
        while True:
            try:
                results = self.get_latest_results()
                if results:
                    report = self.format_status_report(results)
                    print("\033[2J\033[H")  # Clear screen
                    print(report)
                time.sleep(30)  # Update every 30 seconds
            except KeyboardInterrupt:
                logging.info("Monitoring stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in monitoring: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    monitor = ModelMonitor()
    monitor.monitor()
