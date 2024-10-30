# Fine-tuning and Evaluation of GPT Models for Scratch Project Analysis

## Abstract
This technical report presents a comprehensive analysis of the fine-tuning process and evaluation methodology applied to OpenAI's GPT models for Scratch project analysis. We detail the hyperparameters, dataset characteristics, and evaluation metrics used in training and assessing model performance on the task of understanding and describing Scratch projects.

## 1. Dataset Characteristics

### 1.1 Project Selection Criteria
Projects were selected based on a sophisticated complexity scoring system that evaluates multiple dimensions of Scratch project sophistication:

1. **Block Usage Complexity**
   - Custom block definitions and implementations
   - Control structures (loops, conditionals)
   - Event handling mechanisms
   - Variable and list operations

2. **Interaction Complexity**
   - Sprite-to-sprite communications
   - Broadcast mechanisms
   - Stage-sprite interactions
   - Clone operations

### 1.2 Dataset Statistics
Based on our analysis of the TUDelft Scratch Dataset, we identified several highly complex projects:

- Highest Complexity Score: 13,459 (Project ID: 25142995)
- Second Highest: 10,981 (Project ID: 25772183)
- Third Highest: 10,814 (Project ID: 16661984)

Representative Project Statistics (Project ID: 25142995):
- Total Blocks: 21,369
- Sprites: 286
- Custom Blocks: 2,664
- Control Blocks: 1,999
- Variables: 301
- Lists: 108
- Broadcasts: 40
- Interactions: 19

Block Distribution Highlights:
- Control Structures: 2,740 blocks (doIf, doIfElse, doRepeat)
- Custom Procedures: 2,664 blocks
- Variable Operations: 1,898 setVar operations
- List Operations: 846 list manipulation blocks
- Event Handlers: 104 broadcast receivers

## 2. Fine-tuning Configuration

### 2.1 Model Architectures
Two primary models were fine-tuned:
1. GPT-4o (2024-08-06)
2. GPT-4o-mini (2024-07-18)

### 2.2 Training Jobs
Multiple fine-tuning jobs were executed:

GPT-4o (2024-08-06):
- Successful job: ftjob-YkK6KO5rrK2I9gMi2lt8TEj7
- Duration: ~4.85 hours (1728072521 to 1728077371)

GPT-4o-mini (2024-07-18):
- Three successful jobs:
  1. ftjob-Y8tpqHQDTMGu3eENQcZdkkjX (~47 minutes)
  2. ftjob-xRjdK7exCwTnpEvqTjcQY8XJ (~47 minutes)
  3. ftjob-Bp6wX5EuQGiEDYQr1HyP62t0 (~58 minutes)

### 2.3 Training Parameters
- Learning Rate: 0.1
- Batch Size: 4
- Epochs: 5
- Maximum Sequence Length: 2048
- Context Window: 8192 tokens

## 3. Evaluation Results

### 3.1 Baseline Performance
- Accuracy: 0.56
- Mean Squared Error: 0.21

### 3.2 Model Performance

GPT-4o (2024-08-06):
- Accuracy: 0.0 (-0.56 vs baseline)
- MSE: 2,116.0 (+2,115.79 vs baseline)

GPT-4o-mini (2024-07-18):
- Accuracy: 0.0 (-0.56 vs baseline)
- MSE: 9,409.0 (+9,408.79 vs baseline)

### 3.3 Error Analysis

Common error patterns observed:
1. Sprite Misidentification
   - Models consistently identify "Sprite1" instead of "Stage"
   - GPT-4o-mini adds additional position information not present in expected output

2. Format Inconsistency
   - Models add verbose prefixes ("This Scratch project contains...")
   - GPT-4o-mini includes detailed but incorrect position coordinates

3. Response Structure
   - Both models deviate from the expected minimal format
   - Additional metadata included unnecessarily

## 4. Discussion

### 4.1 Current Limitations
1. Format Adherence
   - Models fail to maintain the simple expected output format
   - Additional verbosity introduces errors

2. Accuracy Issues
   - Zero accuracy across both models
   - Significant regression from baseline performance

3. Model Differences
   - GPT-4o shows lower MSE despite same accuracy
   - GPT-4o-mini adds more spurious details

### 4.2 Recommendations
1. Training Data Refinement
   - Enforce stricter output format
   - Include more diverse sprite configurations
   - Balance stage vs sprite examples

2. Model Configuration
   - Adjust temperature and sampling parameters
   - Experiment with different learning rates
   - Consider longer training duration

3. Evaluation Metrics
   - Implement partial matching scores
   - Consider semantic similarity metrics
   - Add structure-aware evaluation

## 5. Conclusion
While the current results show significant room for improvement, the analysis provides clear directions for enhancement. The high complexity of the training projects (up to 13,459 complexity score) suggests rich information available for learning. Future iterations should focus on format consistency and accurate sprite identification while maintaining the ability to process complex project structures.
