import json
import csv
import time
from collections import Counter

def load_analysis_results(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def read_csv_line_by_line(file_path):
    import sys
    csv.field_size_limit(sys.maxsize)  # Set field size limit to maximum possible value
    with open(file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            yield row

def select_representative_projects(allblocks_path, analysis_results, num_projects=1000):
    common_block_types = set(analysis_results['block_types'].keys())
    common_project_structures = [tuple(eval(k)) for k in analysis_results['project_structures'].keys()]

    project_scores = Counter()
    current_project = None
    current_project_blocks = set()

    total_rows = sum(1 for _ in read_csv_line_by_line(allblocks_path))
    processed_rows = 0
    last_log_time = time.time()

    for row in read_csv_line_by_line(allblocks_path):
        try:
            processed_rows += 1
            if time.time() - last_log_time > 5:  # Log every 5 seconds
                print(f"Processed {processed_rows}/{total_rows} rows ({processed_rows/total_rows*100:.2f}%)")
                last_log_time = time.time()

            project_id, _, _, _, _, _, _, opcode, *params = row + [None] * (11 - len(row))

            if current_project != project_id:
                if current_project is not None:
                    # Score the project based on common block types and structures
                    project_scores[current_project] += len(current_project_blocks & common_block_types)
                    if tuple(sorted(current_project_blocks)) in common_project_structures:
                        project_scores[current_project] += 10  # Bonus for matching common structure

                current_project = project_id
                current_project_blocks = set()

            if opcode:
                current_project_blocks.add(opcode)

        except Exception as e:
            print(f"Error processing row {processed_rows}: {e}")
            continue

    # Score the last project
    if current_project is not None:
        project_scores[current_project] += len(current_project_blocks & common_block_types)
        if tuple(sorted(current_project_blocks)) in common_project_structures:
            project_scores[current_project] += 10

    print(f"Finished processing {processed_rows} rows. Selecting top projects...")

    # Select the top scoring projects
    representative_projects = [project for project, _ in project_scores.most_common(num_projects)]
    return representative_projects

if __name__ == "__main__":
    analysis_results_path = "block_analysis_results.json"
    allblocks_path = "/home/ubuntu/keto_app_clone/keto_app/allBlocks.csv"

    print("Loading analysis results...")
    analysis_results = load_analysis_results(analysis_results_path)

    print("Selecting representative projects...")
    representative_projects = select_representative_projects(allblocks_path, analysis_results)

    print(f"Selected {len(representative_projects)} representative projects.")

    # Save the list of representative project IDs
    with open("representative_projects.json", "w") as f:
        json.dump(representative_projects, f, indent=2)

    print("Representative project IDs saved to representative_projects.json")
