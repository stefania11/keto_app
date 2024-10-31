# Model Evaluation Comparison
Generated at: 2024-10-31 21:32:28

| Model          | Projects Evaluated   |   Average Semantic Similarity | Status   |
|:---------------|:---------------------|------------------------------:|:---------|
| Claude-3-haiku | 30/30                |                        0.5495 | Complete |
| Gemini-Pro     | 30/30                |                        0.598  | Complete |
| DeepSeek-Coder | 30/30                |                        0.6156 | Complete |

## Notes:
- All evaluations performed on the same set of 30 medium-complexity projects
- Semantic similarity calculated using SentenceTransformer (all-MiniLM-L6-v2)
- All models configured with temperature=0.2 for consistent output format
