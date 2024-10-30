# Documentation of Selected Projects and JSON Structure

## Selected Projects for Fine-Tuning

The following criteria were used to select the best projects for fine-tuning:
- **Complexity**: Projects with a higher number of blocks, scripts, and sprites were prioritized.
- **Diversity**: Projects that utilized a wide range of block types, including custom blocks, were selected.
- **Use of Variables and Lists**: Projects that made use of variables and lists were considered valuable for training.
- **Extensions**: Projects that included extensions were included to ensure a comprehensive dataset.

The selected projects are documented in the `selected_projects.json` file, which contains the IDs and analysis results of the chosen projects.

## Simplified JSON File Structure

The JSON file structure was simplified to enhance efficiency and manageability. The following changes were made:
- Removed redundant fields such as `costumesCount`, `soundsCount`, and `commentsCount`.
- Consolidated block information into a single `blocks` object containing `total`, `unique`, and `frequency` data.
- Retained essential fields such as `scripts`, `sprites`, `variables`, `lists`, and `extensions`.

The simplified structure is exemplified in the `complex_analysis.json` file, which now contains only the necessary data for project analysis.

This documentation serves as a reference for the selection process and the JSON structure modifications, ensuring clarity and consistency in project management.
