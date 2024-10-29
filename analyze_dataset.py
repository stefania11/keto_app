import os
import gc
import sys
import json
import traceback
from typing import Dict, Generator, List, Tuple
from pathlib import Path
import pandas as pd
import requests
from tqdm import tqdm

def download_file(url: str, file_path: Path, chunk_size: int = 8192) -> bool:
    """Download a file in chunks with progress indication."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = chunk_size
        written = 0

        with open(file_path, 'wb') as f:
            for data in response.iter_content(chunk_size=block_size):
                written += len(data)
                f.write(data)
                if total_size:
                    progress = int(50 * written / total_size)
                    sys.stdout.write(f'\rDownloading: [{"=" * progress}{" " * (50-progress)}] {written}/{total_size} bytes')
                    sys.stdout.flush()
        print("\nDownload complete!")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def process_csv_in_chunks(file_path: Path) -> Generator[pd.DataFrame, None, None]:
    """Process CSV file in chunks, yielding one project at a time."""
    chunk_size = 1000
    current_project_rows = []
    current_project_id = None

    csv_params = {
        'chunksize': chunk_size,
        'on_bad_lines': 'skip',
        'names': ['ProjectId', 'Coordinates', 'SpriteIndex', 'Type',
                 'SpriteName', 'ScriptId', 'BlockIndex', 'Block',
                 'Param1', 'Param2', 'Param3'],
        'dtype': {
            'ProjectId': str,
            'SpriteName': str,
            'Block': str,
            'Param1': str,
            'Param2': str,
            'Param3': str
        },
        'na_values': [''],
        'keep_default_na': False,
        'low_memory': True,
        'quoting': 1,  # QUOTE_ALL
        'escapechar': '\\'
    }

    total_rows = 0
    try:
        for chunk in pd.read_csv(file_path, **csv_params):
            total_rows += len(chunk)
            print(f"\rProcessing row {total_rows:,}", end='')

            # Process each project
            for project_id, project_group in chunk.groupby('ProjectId'):
                if pd.notna(project_id):
                    yield project_group.copy()

            # Clear memory
            del chunk
            gc.collect()
    except Exception as e:
        print(f"\nError processing CSV: {e}")
        traceback.print_exc()

def calculate_complexity_score(project_data: pd.DataFrame) -> Tuple[int, Dict[str, int], int]:
    """Calculate complexity score for a project."""
    block_counts = {}
    sprite_names = set()

    # Define block weights with higher emphasis on sophisticated features
    weights = {
        # Custom blocks (highest weight)
        'procDef': 50,           # Custom block definition
        'call': 20,              # Custom block call

        # Control structures
        'doForever': 15,         # Forever loop
        'doRepeat': 15,          # Repeat loop
        'doIf': 15,             # If condition
        'doIfElse': 15,         # If-else condition
        'doUntil': 15,          # Repeat until

        # Variables and Lists
        'setVar:to:': 15,       # Set variable
        'changeVar:by:': 15,    # Change variable
        'append:toList:': 15,   # Add to list
        'deleteLine:ofList:': 15, # Delete from list
        'insert:at:ofList:': 15,  # Insert into list

        # Events and Broadcasting
        'broadcast:': 15,        # Send broadcast
        'whenIReceive': 15,      # Receive broadcast

        # Sensing and Interactions
        'touching:': 10,         # Touch detection
        'touchingColor:': 10,    # Color touch detection
        'keyPressed:': 10,       # Key press detection
        'mousePressed': 10,      # Mouse click detection

        # Motion and Looks (lower weights)
        'forward:': 5,
        'turnRight:': 5,
        'turnLeft:': 5,
        'heading:': 5,
        'pointTowards:': 5,
        'gotoX:y:': 5,
        'changeXposBy:': 5,
        'changeYposBy:': 5,
        'xpos:': 5,
        'ypos:': 5
    }

    # Count blocks and sprites
    for _, row in project_data.iterrows():
        block_type = row['Block']
        sprite_name = row['SpriteName']

        if pd.notna(sprite_name):
            sprite_names.add(sprite_name)

        if pd.notna(block_type):
            block_counts[block_type] = block_counts.get(block_type, 0) + 1

    # Calculate base score from weighted blocks
    score = sum(count * weights.get(block_type, 1)
               for block_type, count in block_counts.items())

    # Add bonuses for project characteristics
    sprite_count = len(sprite_names)
    total_blocks = sum(block_counts.values())

    # Bonus for custom blocks and procedure calls
    custom_block_count = block_counts.get('procDef', 0)
    procedure_calls = block_counts.get('call', 0)
    if custom_block_count > 0:
        score += custom_block_count * 100  # Major bonus for custom blocks
        score += procedure_calls * 30      # Bonus for using custom blocks

    # Bonus for varied control structures
    control_blocks = sum(block_counts.get(block, 0) for block in
                        ['doForever', 'doRepeat', 'doIf', 'doIfElse', 'doUntil'])
    if control_blocks > 0:
        score += control_blocks * 15

    # Bonus for broadcasts and events
    broadcast_count = (block_counts.get('broadcast:', 0) +
                      block_counts.get('whenIReceive', 0))
    if broadcast_count > 0:
        score += broadcast_count * 20

    # Bonus for sprite interactions
    interaction_blocks = sum(block_counts.get(block, 0) for block in
                           ['touching:', 'touchingColor:', 'keyPressed:'])
    if interaction_blocks > 0:
        score += interaction_blocks * 15

    # Bonus for multiple sprites
    if sprite_count > 1:
        score += sprite_count * 25

    # Bonus for project size and complexity
    if total_blocks > 50:
        score += int((total_blocks - 50) * 1.5)

    return score, block_counts, sprite_count

def format_project_description(project_id: int, complexity_data: Tuple[int, Dict[str, int], int]) -> Dict[str, str]:
    """Format project data for the fine-tuning dataset."""
    score, block_counts, sprite_count = complexity_data

    # Calculate specific metrics
    custom_blocks = block_counts.get('procedures_definition', 0)
    control_blocks = sum(block_counts.get(block, 0) for block in
                        ['control_if', 'control_if_else', 'control_repeat', 'control_repeat_until', 'control_forever'])
    variables = block_counts.get('data_variable', 0)
    lists = block_counts.get('data_list', 0)
    broadcasts = block_counts.get('event_broadcast', 0)
    stage_interactions = sum(block_counts.get(block, 0) for block in
                           ['sensing_touchingobject', 'sensing_touchingcolor', 'sensing_coloristouchingcolor'])
    total_blocks = sum(block_counts.values())

    return {
        "prompt": f"Describe Scratch project ID {project_id}.",
        "completion": f" blocks: {total_blocks}\nsprites: {sprite_count}\ncustom blocks: {custom_blocks}\ncontrol blocks: {control_blocks}\nvariables: {variables}\nlists: {lists}\nbroadcasts: {broadcasts}\nstage interactions: {stage_interactions}"
    }

def save_project(project_data: Dict[str, str], output_file: Path) -> None:
    """Save a project to the output file."""
    with open(output_file, 'a') as f:
        f.write(json.dumps(project_data) + '\n')

def main():
    """Main function to process the dataset and save complex projects."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs('dataset_raw', exist_ok=True)

        # Download required files if they don't exist
        csv_files = [
            'allBlocks.csv',
            'scripts.csv',
            'properties.csv'
        ]

        for file in csv_files:
            if not os.path.exists(f'dataset_raw/{file}'):
                print(f"Downloading {file}...")
                download_file(f'https://raw.githubusercontent.com/TUDelftScratchLab/ScratchDataset/master/Dataset/CSV%20files/{file}',
                            f'dataset_raw/{file}')

        # Process the dataset
        print("\nAnalyzing projects...")
        complex_projects = []
        project_analysis = []

        # Process CSV in chunks
        for project_id, project_data in process_csv_in_chunks('dataset_raw/allBlocks.csv'):
            # Calculate complexity score and get block information
            score, block_counts, sprite_count = calculate_complexity_score(project_data)

            # Get important metrics
            custom_block_count = block_counts.get('procDef', 0)
            procedure_calls = block_counts.get('call', 0)
            control_blocks = sum(block_counts.get(block, 0) for block in
                               ['doRepeat', 'doForever', 'doIf', 'doIfElse'])
            broadcast_count = (block_counts.get('broadcast:', 0) +
                             block_counts.get('whenIReceive', 0))
            interaction_blocks = sum(block_counts.get(block, 0) for block in
                                   ['touching:', 'touchingColor:'])
            total_blocks = sum(block_counts.values())

            # Project must meet ALL of these criteria:
            if (custom_block_count > 0 and          # Must have custom blocks
                score >= 500 and                    # Minimum complexity score
                total_blocks >= 100 and             # Minimum block count
                sprite_count >= 3 and               # Multiple sprites
                control_blocks >= 5 and             # Must use control structures
                (broadcast_count > 0 or             # Must have either broadcasts
                 interaction_blocks > 0)):          # or sprite interactions

                # Format project for the dataset
                formatted_project = format_project_description(
                    project_id, (score, block_counts, sprite_count))
                complex_projects.append(formatted_project)

                # Save analysis data
                project_analysis.append({
                    "project_id": project_id,
                    "score": score,
                    "total_blocks": total_blocks,
                    "sprite_count": sprite_count,
                    "custom_blocks": custom_block_count,
                    "control_blocks": control_blocks,
                    "broadcasts": broadcast_count,
                    "interactions": interaction_blocks,
                    "procedure_calls": procedure_calls
                })

                # Print progress for significant finds
                print(f"\nFound complex project {project_id}:")
                print(f"Score: {score}")
                print(f"Custom blocks: {custom_block_count}")
                print(f"Total blocks: {total_blocks}")
                print(f"Sprites: {sprite_count}")
                print(f"Control blocks: {control_blocks}")
                print(f"Broadcasts: {broadcast_count}")
                print(f"Interactions: {interaction_blocks}")
                print("-" * 50)

        # Save results
        print(f"\nSaving {len(complex_projects)} complex projects...")
        save_project(complex_projects, 'complex_projects_formatted.json')

        print("Saving project analysis...")
        with open('project_complexity_analysis.json', 'w') as f:
            json.dump(project_analysis, f, indent=2)

        print("\nAnalysis complete!")
        print(f"Found {len(complex_projects)} complex projects")
        print("Results saved to:")
        print("- complex_projects_formatted.json")
        print("- project_complexity_analysis.json")

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
