import pandas as pd
import json
from pathlib import Path
import numpy as np
from tqdm import tqdm
import os

def process_blocks_in_chunks(chunk_size=10000):
    """Process allBlocks.csv in chunks to identify medium complexity projects."""
    projects_data = {}
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
        chunksize=chunk_size,
        on_bad_lines="skip"
    )

    print("Processing blocks data in chunks...")
    for chunk in tqdm(chunk_iterator):
        for project_id, project_blocks in chunk.groupby("ProjectId"):
            if project_id not in projects_data:
                # Calculate complexity metrics
                total_blocks = len(project_blocks)
                unique_targets = len(project_blocks["Target"].unique())
                control_blocks = len(project_blocks[project_blocks["Type"].str.contains("control", na=False)])
                custom_blocks = len(project_blocks[project_blocks["Type"].str.contains("custom", na=False)])

                # Calculate complexity score
                complexity_score = (
                    total_blocks * 0.5 +
                    unique_targets * 2.0 +
                    control_blocks * 1.5 +
                    custom_blocks * 3.0
                )

                # Store project data if it meets medium complexity criteria
                if 100 <= complexity_score <= 200:
                    projects_data[project_id] = {
                        "ProjectId": project_id,
                        "ComplexityScore": complexity_score,
                        "TotalBlocks": total_blocks,
                        "UniqueTargets": unique_targets,
                        "ControlBlocks": control_blocks,
                        "CustomBlocks": custom_blocks
                    }

    # Convert to DataFrame and sort by complexity
    projects_df = pd.DataFrame.from_dict(projects_data, orient='index')
    projects_df = projects_df.sort_values("ComplexityScore", ascending=False)

    # Save medium complexity projects
    os.makedirs("src/data", exist_ok=True)
    projects_df.to_csv("src/data/medium_complexity_projects.csv", index=False)
    print(f"Found {len(projects_df)} medium complexity projects")
    return projects_df

if __name__ == "__main__":
    process_blocks_in_chunks()
