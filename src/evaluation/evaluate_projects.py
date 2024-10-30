import pandas as pd
import json
import sys
from pathlib import Path
import numpy as np
from tqdm import tqdm
import os

def load_medium_complexity_projects():
    """Load the identified medium complexity projects."""
    projects_df = pd.read_csv("src/data/medium_complexity_projects.csv")
    return projects_df.sort_values("ComplexityScore", ascending=False)

def prepare_project_data(project_id, blocks_df):
    """Prepare project data in the required format."""
    project_blocks = blocks_df[blocks_df["ProjectId"] == project_id]

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
        projects_df = load_medium_complexity_projects()
        if len(projects_df) < num_projects:
            print(f"Warning: Only {len(projects_df)} projects available")
            num_projects = len(projects_df)

        selected_projects = projects_df.head(num_projects)

        # Load blocks data
        print("Loading blocks data...")
        blocks_df = pd.read_csv(
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
            on_bad_lines="skip"
        )

        # Prepare evaluation data
        print("Preparing evaluation data...")
        evaluation_data = []
        for _, project in tqdm(selected_projects.iterrows(), total=len(selected_projects)):
            project_data = prepare_project_data(project["ProjectId"], blocks_df)
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
