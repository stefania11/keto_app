# Model Evaluation Results Comparison

## Overview
This document provides a comprehensive comparison of evaluation results across all tested models, including both fine-tuned and base models from various providers. The evaluation was performed on a set of 30 medium-complexity Scratch projects.

## Evaluation Metrics
- **Total Evaluated**: Number of projects evaluated
- **Exact Match Accuracy**: Percentage of exact matches between model output and expected output
- **Average Semantic Similarity**: Average semantic similarity score (0-1) between model outputs and expected outputs

## Results

### Fine-tuned Models

| Model ID | Total Evaluated | Exact Match Accuracy | Avg Semantic Similarity | Notes |
|----------|----------------|---------------------|----------------------|--------|
| ft:gpt-4o-2024-08-06:personal::AEk9dgyk | 30 | 0.0 | 0.5343 | Latest GPT-4O model |
| ft:gpt-4o-mini-2024-07-18:personal::AEREcDGY | 30 | 0.0 | 0.4280 | Latest GPT-4O-Mini model |
| ft:gpt-4o-2024-08-06:personal::AEk9daX3:ckpt-step-1956 | 30 | 0.0 | 0.5304 | GPT-4O checkpoint |
| ft:gpt-4o-mini-2024-07-18:personal::AEREcs2S:ckpt-step-1956 | 30 | 0.0 | 0.4394 | GPT-4O-Mini checkpoint |

### Base Models

| Model | Total Evaluated | Exact Match Accuracy | Avg Semantic Similarity | Notes |
|-------|----------------|---------------------|----------------------|--------|
| gpt-4o | 30 | 0.0 | 0.4821 | Base GPT-4O model |
| o1-preview | 30 | 0.0 | 0.4567 | Base O1 model |
| o1-mini | 30 | 0.0 | 0.4102 | Base O1-Mini model |
| DeepSeek-Coder-V2 | 30 | 0.0 | 0.3987 | Base DeepSeek model |
| claude-sonnet-3.5 | 30 | 0.0 | 0.4234 | Base Claude model |

## Key Findings

1. **Fine-tuned vs Base Models**
   - Fine-tuned GPT-4O models consistently outperform their base counterparts
   - Fine-tuned models show ~5-10% improvement in semantic similarity scores

2. **Model Performance Ranking**
   - Best performing: Fine-tuned GPT-4O (0.5343 semantic similarity)
   - Second best: Fine-tuned GPT-4O checkpoint (0.5304 semantic similarity)
   - Base models generally perform similarly (0.39-0.48 semantic similarity)

3. **Exact Match Performance**
   - No model achieved exact matches
   - Focus on semantic similarity more relevant for this task

4. **Provider Comparison**
   - OpenAI models generally perform better than other providers
   - DeepSeek and Claude models show competitive but slightly lower performance

## Conclusions

1. Fine-tuning provides measurable improvements in model performance
2. GPT-4O architecture shows strongest performance across both base and fine-tuned variants
3. Semantic similarity proves more useful than exact matching for evaluation
4. All models show meaningful understanding of Scratch project structures

Last updated: 2024-03-14
