import json
import os

def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def format_for_chat_model(project):
    system_message = "You are an AI assistant that understands Scratch projects and can describe their structure."
    user_message = f"Describe the structure of this Scratch project with ID {project['project_id']}."
    blocks = [f"{block['type']}: {block['name']}" for block in project['blocks']]
    assistant_message = f"This Scratch project contains the following blocks:\n" + "\n".join(blocks)
    return {
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message}
        ]
    }

def prepare_dataset(input_file, output_file):
    data = load_json_data(input_file)
    formatted_data = [format_for_chat_model(project) for project in data]

    with open(output_file, 'w') as f:
        for item in formatted_data:
            json.dump(item, f)
            f.write('\n')

if __name__ == "__main__":
    input_file = "sampled_projects.json"
    output_file = "prepared_dataset.jsonl"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        exit(1)

    prepare_dataset(input_file, output_file)
    print(f"Dataset prepared and saved to {output_file}")
