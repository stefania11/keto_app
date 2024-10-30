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
        # Convert ProjectId to string and ensure it's in the correct format
        projects_df['ProjectId'] = projects_df['ProjectId'].astype(str)
        project_ids = set(projects_df["ProjectId"])
        print(f"Selected project IDs: {project_ids}")

        # Process blocks data in chunks
        print("Processing blocks data...")
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

        # Initialize storage for project blocks
        project_blocks = {pid: [] for pid in project_ids}
        total_blocks_found = {pid: 0 for pid in project_ids}

        print("\nReading blocks and matching projects...")
        for chunk in tqdm(chunk_iterator, desc="Reading blocks"):
            # Filter chunk for our projects
            mask = chunk["ProjectId"].isin(project_ids)
            if mask.any():
                filtered_chunk = chunk[mask]
                print(f"\nFound matching projects in chunk: {filtered_chunk['ProjectId'].unique()}")
                for pid in project_ids:
                    project_chunk = filtered_chunk[filtered_chunk["ProjectId"] == pid]
                    if not project_chunk.empty:
                        project_blocks[pid].append(project_chunk)
                        total_blocks_found[pid] += len(project_chunk)

        print("\nBlocks found per project:")
        for pid, count in total_blocks_found.items():
            print(f"Project {pid}: {count} blocks")

        # Sample some raw data for debugging
        print("\nSampling raw data from allBlocks.csv...")
        sample_df = pd.read_csv(
            "src/data/dataset_raw/allBlocks.csv",
            names=["ProjectId", "BlockId", "ParentId", "Type", "Target",
                  "OpCode", "NextBlock", "Comment", "Input"],
            nrows=5
        )
        print("\nSample data from allBlocks.csv:")
        print(sample_df[["ProjectId", "BlockId"]].head())

        # Prepare evaluation data
        print("\nPreparing evaluation data...")
        evaluation_data = []
        for pid in tqdm(project_ids, desc="Processing projects"):
            if project_blocks[pid]:
                combined_blocks = pd.concat(project_blocks[pid])
                print(f"\nProcessing project {pid}:")
                print(f"Total blocks: {len(combined_blocks)}")
                print(f"Unique targets: {combined_blocks['Target'].unique()}")
                project_data = prepare_project_data(pid, combined_blocks)
                if project_data:
                    evaluation_data.append(project_data)
                else:
                    print(f"Project {pid} data preparation failed")

        # Save evaluation data
        output_file = "src/data/evaluation_data.jsonl"
        print(f"\nSaving evaluation data to {output_file}...")
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
