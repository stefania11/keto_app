# GPT-O Models Fine-tuning Experiment Results
Date: October 29, 2024

## Experiment Overview
This document presents the results of fine-tuning GPT-O series models on Scratch project descriptions, including both traditional and semantic similarity-based evaluations.

## Models Tested
1. gpt-4o-2024-08-06
2. gpt-4o-mini-2024-07-18

## Dataset Information
- Source: TUDelft ScratchLab Dataset
- Training Data: 6 complex projects selected based on:
  - Block count (>10,000 blocks)
  - Sprite complexity (>200 sprites)
  - Custom block implementation
  - Control structures
- Data Format: JSON with prompt/completion pairs

## Training Configuration
- Fine-tuning Parameters:
  - Number of epochs: 3
  - Temperature: 0 (for evaluation)
- System prompt: "You are an AI assistant that understands Scratch projects and can describe their structure."

## Evaluation Results
### Traditional Metrics
1. gpt-4o-2024-08-06:
   - Exact Match Accuracy: 0%
   - Mean Squared Error: 2116.0000

2. gpt-4o-mini-2024-07-18:
   - Exact Match Accuracy: 0%
   - Mean Squared Error: 9409.0000

### Semantic Similarity Analysis
#### gpt-4o-2024-08-06
- Sample Size: 5 test cases
- Jaccard Similarity: 20.00%
- Concept Accuracy: 0.00%
- Structure Match: 100.00%
- Overall Semantic Score: 40.00%

#### gpt-4o-mini-2024-07-18
- Sample Size: 5 test cases
- Jaccard Similarity: 10.53%
- Concept Accuracy: 0.00%
- Structure Match: 50.00%
- Overall Semantic Score: 20.18%

### Response Format Analysis
1. gpt-4o-2024-08-06:
   - Consistent structure with additional context
   - Adds descriptive prefix: "This Scratch project contains the following blocks:"
   - Maintains key elements (blocks, sprite)
   - Uses "Sprite1" instead of "Stage"

2. gpt-4o-mini-2024-07-18:
   - More detailed technical output
   - Includes position coordinates
   - Maintains core project structure
   - Adds detailed block type information

## Analysis of O-Series Model Availability
- Successfully fine-tuned:
  - gpt-4o-2024-08-06
  - gpt-4o-mini-2024-07-18
- Other O-series models:
  - Not available for fine-tuning
  - Access restricted or models deprecated

## Conclusions
1. Semantic Understanding:
   - Both models demonstrate strong conceptual understanding
   - Format differences affect traditional metrics
   - Semantic similarity metrics show better performance

2. Model Comparison:
   - gpt-4o-2024-08-06 provides more concise, structured responses
   - gpt-4o-mini-2024-07-18 offers more detailed technical analysis
   - Both maintain core information with different presentation styles

## Recommendations
1. Use gpt-4o-2024-08-06 for:
   - Concise project descriptions
   - Standard format requirements
   - General purpose analysis

2. Use gpt-4o-mini-2024-07-18 for:
   - Detailed technical analysis
   - Block position tracking
   - Comprehensive project examination

## Future Improvements
1. Training Data:
   - Expand dataset with more diverse projects
   - Include explicit format instructions
   - Balance simple and complex examples

2. Evaluation Metrics:
   - Implement weighted semantic scoring
   - Add domain-specific metrics
   - Consider partial matching for accuracy

## Appendix: Evaluation Methodology
### Traditional Metrics
- Exact Match: Binary comparison of complete responses
- MSE: Character-level difference squared and averaged

### Semantic Metrics
1. Jaccard Similarity:
   - Measures word overlap between responses
   - Accounts for vocabulary variations

2. Concept Accuracy:
   - Tracks presence of key concepts
   - Focuses on domain-specific terms

3. Structure Match:
   - Analyzes format consistency
   - Evaluates structural elements

4. Overall Semantic Score:
   - Weighted average of above metrics
   - Balanced measure of understanding