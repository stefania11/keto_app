import csv
from collections import Counter
import json

# Increase the field size limit
csv.field_size_limit(1000000)  # Set to a larger value, e.g., 1 million

def read_csv_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            yield row

def analyze_blocks(file_path):
    block_types = Counter()
    project_structures = Counter()
    current_project = None
    current_project_blocks = set()

    for row in read_csv_line_by_line(file_path):
        try:
            project_id, _, _, _, _, _, _, opcode, *params = row + [None] * (11 - len(row))

            if current_project != project_id:
                if current_project is not None:
                    project_structures[tuple(sorted(current_project_blocks))] += 1
                current_project = project_id
                current_project_blocks = set()

            if opcode:
                block_types[opcode] += 1
                current_project_blocks.add(opcode)

        except Exception as e:
            print(f"Error processing row: {e}")
            continue

    # Add the last project's structure
    if current_project_blocks:
        project_structures[tuple(sorted(current_project_blocks))] += 1

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
