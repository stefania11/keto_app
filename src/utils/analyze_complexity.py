import pandas as pd
import numpy as np

def calculate_complexity_score(project_data):
    """Calculate complexity score for a project based on various metrics."""
    score = 0

    # Base metrics
    if isinstance(project_data, dict):
        if 'total_blocks' in project_data:
            score += project_data['total_blocks'] * 0.5
        if 'custom_blocks' in project_data:
            score += project_data['custom_blocks'] * 2
        if 'control_blocks' in project_data:
            score += project_data['control_blocks'] * 1.5
        if 'variables' in project_data:
            score += project_data['variables'] * 1
        if 'lists' in project_data:
            score += project_data['lists'] * 1.5
        if 'broadcasts' in project_data:
            score += project_data['broadcasts'] * 1
        if 'sprites' in project_data:
            score += project_data['sprites'] * 0.5

    return score

def is_medium_complexity(score):
    """Determine if a project is of medium complexity."""
    # Medium complexity range: 100-500
    return 100 <= score <= 500

