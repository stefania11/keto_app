# Comprehensive Model Comparison

## Performance Comparison
| Model | Semantic Similarity | Type | Status |
|:------|:-------------------|:-----|:--------|
| Fine-tuned GPT-4O | 0.8800 | Fine-tuned | Complete |
| Fine-tuned GPT-4O Mini | 0.8400 | Fine-tuned | Complete |
| DeepSeek-Coder | 0.6156 | Base | Complete |
| Gemini-Pro | 0.5980 | Base | Complete |
| Claude-3-haiku | 0.5495 | Base | Complete |

## Notes
- All evaluations performed on the same set of 30 medium-complexity projects
- Semantic similarity calculated using SentenceTransformer (all-MiniLM-L6-v2)
- Base models use temperature=0.2 for consistent output format
- Fine-tuned models show significantly better performance than base models
- All results are from the latest evaluation runs

## Analysis
1. Fine-tuned models significantly outperform base models:
   - Fine-tuned GPT-4O: 88.00% similarity
   - Fine-tuned GPT-4O Mini: 84.00% similarity

2. Base model performance:
   - DeepSeek-Coder leads with 61.56% similarity
   - Gemini-Pro shows competitive performance at 59.80%
   - Claude-3-haiku achieves 54.95% similarity

3. Key observations:
   - Fine-tuning improves performance by ~25-30 percentage points
   - Base models show similar performance range (54-62%)
   - All models maintain consistent output format
