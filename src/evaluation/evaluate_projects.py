import pandas as pd
import json
import sys
from pathlib import Path
import numpy as np
from tqdm import tqdm
import os

def load_medium_complexity_projects(num_projects=30):
    """Load the identified medium complexity projects."""
    projects_df = pd.read_csv("src/data/medium_complexity_projects.csv")
    projects_df = projects_df.sort_values("ComplexityScore", ascending=False)
    return projects_df.head(num_projects)

def process_project_blocks(project_id, chunk_iterator):
    """Process blocks for a specific project from chunks."""
    project_blocks = []
    for chunk in chunk_iterator:
        project_chunk = chunk[chunk["ProjectId"] == project_id]
        if not project_chunk.empty:
            project_blocks.append(project_chunk)
    return pd.concat(project_blocks) if project_blocks else pd.DataFrame()

def prepare_project_data(project_id, project_blocks):
    """Prepare project data in the required format."""
    if project_blocks.empty:
        return None

    # Extract sprites and their blocks
    sprites = {}
    for target in project_blocks["Target"].unique():
        sprite_blocks = project_blocks[project_blocks["Target"] == target]
        blocks = []
        for _, block in sprite_blocks.iterrows():
            blocks.append({
                "opcode": block["OpCode"],
                "next": block["NextBlock"],
                "parent": block["ParentId"],
                "inputs": block["Input"] if pd.notna(block["Input"]) else None
            })
        sprites[target] = blocks

    return {
        "prompt": f"Describe Scratch project ID {project_id}.",
        "completion": f" blocks:\n" + "\n".join([f"sprite: {sprite}" for sprite in sprites.keys()])
    }

def evaluate_projects(num_projects=30):
    """Evaluate a specified number of medium complexity projects."""
    try:
        # Load projects
        print(f"Loading top {num_projects} medium complexity projects...")
        projects_df = load_medium_complexity_projects(num_projects)

        # Create chunk iterator for blocks data
        chunk_iterator = pd.read_csv(
            "src/data/dataset_raw/allBlocks.csv",
            names=["ProjectId", "BlockId", "ParentId", "Type", "Target",
                  "OpCode", "NextBlock", "Comment", "Input"],
            dtype={
                "ProjectId": str,
                "BlockId": str,
                "ParentId": str,
                "Type": str,
                "Target": str,
                "OpCode": str,
                "NextBlock": str,
                "Comment": str,
                "Input": str
            },
            chunksize=10000,
            on_bad_lines="skip"
        )

        # Prepare evaluation data
        print("Preparing evaluation data...")
        evaluation_data = []
        for _, project in tqdm(projects_df.iterrows(), total=len(projects_df)):
            project_blocks = process_project_blocks(project["ProjectId"], chunk_iterator)
            project_data = prepare_project_data(project["ProjectId"], project_blocks)
            if project_data:
                evaluation_data.append(project_data)

        # Save evaluation data
        output_file = "src/data/evaluation_data.jsonl"
        print(f"Saving evaluation data to {output_file}...")
        with open(output_file, "w") as f:
            for item in evaluation_data:
                f.write(json.dumps(item) + "\n")

        print(f"Successfully prepared {len(evaluation_data)} projects for evaluation")
        return True

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = evaluate_projects(30)
    sys.exit(0 if success else 1)
