import json
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluationAnalyzer:
    def __init__(self):
        self.results_dir = Path('src/evaluation/results')
        self.output_dir = Path('src/evaluation/analysis')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_evaluation_results(self):
        """Load all evaluation results from the results directory."""
        results = []

        # Track progress metrics
        total_projects = {'claude': 13256, 'deepseek': 30, 'gpt2': 9822}

        # Create model-specific result dictionaries to handle duplicates
        model_results = {}

        # Load model evaluation results
        for result_file in self.results_dir.glob('*_evaluation_results_*.json'):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    model_name = data.get('model_name', str(result_file))
                    model_key = model_name.lower().split('-')[0]
                    total = total_projects.get(model_key, 0)
                    progress = (data.get('total_evaluated', 0) / total * 100) if total > 0 else 0

                    # Create result entry
                    result_entry = {
                        'model_name': model_name,
                        'total_evaluated': data.get('total_evaluated', 0),
                        'progress_percentage': f'{progress:.2f}%',
                        'exact_match_accuracy': data.get('exact_match_accuracy', 0),
                        'avg_semantic_similarity': data.get('avg_semantic_similarity', 0),
                        'source': str(result_file),
                        'last_updated': datetime.fromtimestamp(result_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Update model results, keeping only the latest result for each model
                    if model_key not in model_results or \
                       datetime.strptime(result_entry['last_updated'], '%Y-%m-%d %H:%M:%S') > \
                       datetime.strptime(model_results[model_key]['last_updated'], '%Y-%m-%d %H:%M:%S'):
                        model_results[model_key] = result_entry

            except Exception as e:
                logger.error(f'Error loading {result_file}: {str(e)}')

        # Add unique model results to the final results list
        results.extend(model_results.values())

        # Load GPT-2 training progress
        training_log = Path('src/fine_tuning/logs/training_detailed.log')
        if training_log.exists():
            try:
                with open(training_log, 'r') as f:
                    lines = [l for l in f.readlines() if 'Loss' in l]
                    if lines:
                        latest_loss = float(lines[-1].split('Loss = ')[-1].strip())
                        progress = (len(lines) / total_projects['gpt2'] * 100)
                        results.append({
                            'model_name': 'GPT-2',
                            'total_evaluated': len(lines),
                            'progress_percentage': f'{progress:.2f}%',
                            'latest_loss': latest_loss,
                            'source': str(training_log),
                            'last_updated': datetime.fromtimestamp(training_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
            except Exception as e:
                logger.error(f'Error loading GPT-2 training log: {str(e)}')

        # Check Claude evaluation logs
        claude_log = Path('src/evaluation/logs/claude_evaluation.log')
        if claude_log.exists():
            try:
                with open(claude_log, 'r') as f:
                    lines = f.readlines()
                    progress_lines = [l for l in lines if 'Evaluating project' in l]
                    if progress_lines:
                        latest = progress_lines[-1]
                        current = int(latest.split('project ')[1].split('/')[0])
                        total = int(latest.split('/')[1].split()[0])
                        progress = (current / total * 100)
                        results.append({
                            'model_name': 'Claude-3',
                            'total_evaluated': current,
                            'progress_percentage': f'{progress:.2f}%',
                            'source': str(claude_log),
                            'last_updated': datetime.fromtimestamp(claude_log.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        })
            except Exception as e:
                logger.error(f'Error loading Claude evaluation log: {str(e)}')

        return results

    def create_comparison_table(self, results):
        """Create a formatted comparison table of model results."""
        if not results:
            logger.warning('No results to analyze')
            return None

        df = pd.DataFrame(results)

        # Reorder columns for better readability
        columns = ['model_name', 'progress_percentage', 'total_evaluated']
        if 'exact_match_accuracy' in df.columns:
            df['exact_match_accuracy'] = df['exact_match_accuracy'].apply(lambda x: f'{x:.2%}' if isinstance(x, (int, float)) else x)
            columns.append('exact_match_accuracy')
        if 'avg_semantic_similarity' in df.columns:
            df['avg_semantic_similarity'] = df['avg_semantic_similarity'].apply(lambda x: f'{x:.2%}' if isinstance(x, (int, float)) else x)
            columns.append('avg_semantic_similarity')
        if 'latest_loss' in df.columns:
            columns.append('latest_loss')

        columns.extend(['last_updated', 'source'])
        df = df[columns]

        return df

    def save_results(self, df):
        """Save results to markdown and CSV files."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save markdown
        markdown_file = self.output_dir / f'model_comparison_{timestamp}.md'
        with open(markdown_file, 'w') as f:
            f.write('# Model Evaluation Results Comparison\n\n')
            f.write(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            f.write(df.to_markdown(index=False))

        # Save CSV
        csv_file = self.output_dir / f'model_comparison_{timestamp}.csv'
        df.to_csv(csv_file, index=False)

        logger.info(f'Results saved to {markdown_file} and {csv_file}')
        return markdown_file, csv_file

def main():
    try:
        analyzer = ModelEvaluationAnalyzer()
        results = analyzer.load_evaluation_results()
        if results:
            df = analyzer.create_comparison_table(results)
            if df is not None:
                markdown_file, csv_file = analyzer.save_results(df)
                logger.info('Analysis completed successfully')

                # Print current progress to console
                print("\n=== Current Evaluation Progress ===")
                progress_df = df[['model_name', 'progress_percentage', 'total_evaluated']]
                print(progress_df.to_string(index=False))
                print("\nDetailed results saved to:", markdown_file)
        else:
            logger.warning('No evaluation results found')
    except Exception as e:
        logger.error(f'Error in analysis: {str(e)}')
        logger.exception("Detailed error traceback:")

if __name__ == "__main__":
    main()
