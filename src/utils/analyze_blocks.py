import pandas as pd
import json
from collections import Counter

def read_csv_in_chunks(file_path, chunk_size=10000):
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, delimiter=',', quotechar='"',
                             names=['project_id', 'position', 'sprite_index', 'type', 'name', 'block_index', 'sub_index', 'opcode', 'param1', 'param2', 'param3']):
        yield chunk

def analyze_blocks(file_path):
    block_types = Counter()
    project_structures = Counter()

    for chunk in read_csv_in_chunks(file_path):
        for _, row in chunk.iterrows():
            try:
                opcode = row['opcode']
                if pd.notna(opcode):
                    block_types[opcode] += 1

                # Analyze project structure
                structure = tuple(sorted(set(chunk[chunk['project_id'] == row['project_id']]['opcode'].dropna())))
                if structure:
                    project_structures[structure] += 1
            except Exception as e:
                print(f"Error processing row: {e}")
                continue

    return block_types, project_structures

def print_top_n(counter, n=10):
    for item, count in counter.most_common(n):
        print(f"{item}: {count}")

if __name__ == "__main__":
    file_path = "/home/ubuntu/keto_app_clone/keto_app/allBlocks.csv"

    print("Analyzing blocks...")
    block_types, project_structures = analyze_blocks(file_path)

    print("\nTop 10 most common block types:")
    print_top_n(block_types)

    print("\nTop 10 most common project structures:")
    print_top_n(project_structures)

    # Save results to a file
    with open("block_analysis_results.json", "w") as f:
        json.dump({
            "block_types": dict(block_types),
            "project_structures": {str(k): v for k, v in project_structures.items()}
        }, f, indent=2)

    print("\nAnalysis complete. Results saved to block_analysis_results.json")
