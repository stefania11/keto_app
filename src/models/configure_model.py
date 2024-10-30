import json
import openai
from openai import OpenAI

# Load the sampled projects
with open('sampled_projects.json', 'r') as f:
    sampled_projects = json.load(f)

# Prepare the dataset in the conversational format required for fine-tuning
def prepare_dataset(projects):
    conversations = []
    for project in projects:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that understands Scratch projects and can describe their structure."},
            {"role": "user", "content": f"Describe the structure of this Scratch project with ID {project['project_id']}."},
            {"role": "assistant", "content": f"This Scratch project with ID {project['project_id']} contains the following blocks:\n"}
        ]
        for block in project['blocks']:
            block_description = f"- Block: {block['name']} (Type: {block['type']}, Position: x={block['x']}, y={block['y']}, z={block['z']})\n"
            messages[-1]["content"] += block_description
        conversations.append({"messages": messages})
    return conversations

dataset = prepare_dataset(sampled_projects)

# Save the prepared dataset
with open('prepared_dataset.jsonl', 'w') as f:
    for conversation in dataset:
        json.dump(conversation, f)
        f.write('\n')

# Set up the OpenAI client
client = OpenAI()

# Create a fine-tuning job
try:
    fine_tuning_job = client.fine_tuning.jobs.create(
        training_file="file-J9ro8w5M3hwIJjdJEaR27NLD",  # Updated with the file ID obtained from the upload
        model="gpt-4o-mini-2024-07-18"
    )
    print(f"Fine-tuning job created: {fine_tuning_job.id}")
except openai.OpenAIError as e:
    print(f"An error occurred: {e}")

print("Fine-tuning job submitted. Monitor the job status using the OpenAI dashboard or API.")
