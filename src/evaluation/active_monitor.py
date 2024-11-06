import json
import time
import logging
from pathlib import Path
from datetime import datetime
import psutil
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('src/evaluation/logs/active_monitor.log')
    ]
)
logger = logging.getLogger(__name__)

def check_process_status(process_name):
    """Check if a process is running by name"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process_name in ' '.join(proc.info['cmdline'] or []):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def analyze_claude_progress():
    """Analyze Claude evaluation progress"""
    results_dir = Path('src/evaluation/results')
    claude_files = list(results_dir.glob('claude_evaluation_intermediate_*.json'))

    if not claude_files:
        return None

    latest_file = max(claude_files, key=lambda x: x.stat().st_mtime)
    with open(latest_file) as f:
        data = json.load(f)

    total_evaluated = data.get('total_evaluated', 0)
    avg_similarity = data.get('avg_semantic_similarity', 0)

    # Calculate rate of progress
    if len(claude_files) > 1:
        sorted_files = sorted(claude_files, key=lambda x: x.stat().st_mtime)
        with open(sorted_files[-2]) as f:
            previous_data = json.load(f)
        previous_total = previous_data.get('total_evaluated', 0)
        time_diff = latest_file.stat().st_mtime - sorted_files[-2].stat().st_mtime
        rate = (total_evaluated - previous_total) / time_diff if time_diff > 0 else 0
    else:
        rate = 0

    return {
        'total_evaluated': total_evaluated,
        'avg_similarity': avg_similarity,
        'completion_percentage': (total_evaluated / 13256) * 100,
        'rate': rate
    }

def analyze_gpt2_progress():
    """Analyze GPT-2 training progress"""
    log_file = Path('src/fine_tuning/logs/training_detailed.log')
    if not log_file.exists():
        return None

    with open(log_file) as f:
        lines = f.readlines()

    progress_info = None
    loss_values = []

    for line in reversed(lines):
        if 'Loss' in line:
            try:
                loss = float(line.split('Loss = ')[-1].strip())
                loss_values.append(loss)
            except ValueError:
                continue
        if '|' in line and '%' in line:
            progress_info = line.strip()
            break

    if not progress_info:
        return None

    try:
        current, total = map(int, progress_info.split('|')[0].strip().split('/'))
        return {
            'current_step': current,
            'total_steps': total,
            'completion_percentage': (current / total) * 100,
            'avg_recent_loss': np.mean(loss_values[:5]) if loss_values else None
        }
    except Exception as e:
        logger.error(f"Error parsing GPT-2 progress: {e}")
        return None

def generate_status_report():
    """Generate comprehensive status report"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Check process status
    claude_running = check_process_status('evaluate_claude.py')
    gpt2_running = check_process_status('train_model_cpu.py')

    # Analyze progress
    claude_progress = analyze_claude_progress()
    gpt2_progress = analyze_gpt2_progress()

    report = f"""=== Active Process Status Report ({timestamp}) ===

1. Claude Evaluation:
   - Process Running: {'Yes' if claude_running else 'No'}"""

    if claude_progress:
        report += f"""
   - Progress: {claude_progress['total_evaluated']}/13256 ({claude_progress['completion_percentage']:.1f}%)
   - Average Similarity: {claude_progress['avg_similarity']:.4f}
   - Processing Rate: {claude_progress['rate']:.2f} items/second"""

    report += f"""

2. GPT-2 Training:
   - Process Running: {'Yes' if gpt2_running else 'No'}"""

    if gpt2_progress:
        report += f"""
   - Progress: {gpt2_progress['current_step']}/{gpt2_progress['total_steps']} ({gpt2_progress['completion_percentage']:.1f}%)
   - Average Recent Loss: {gpt2_progress['avg_recent_loss']:.4f if gpt2_progress['avg_recent_loss'] else 'N/A'}"""

    report += """

3. DeepSeek Evaluation:
   - Status: Complete
   - Results: 30/30 projects processed
   - Average Similarity: 0.6156
   - Exact Match Accuracy: 0.00%

=== End Report ==="""

    # Save report
    report_file = Path('src/evaluation/results/active_status.txt')
    with open(report_file, 'w') as f:
        f.write(report)

    logger.info(report)
    return report

def main():
    """Main monitoring loop"""
    logger.info("Starting active process monitoring")

    while True:
        try:
            generate_status_report()
            time.sleep(60)  # Update every minute
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
            time.sleep(60)

if __name__ == '__main__':
    main()
