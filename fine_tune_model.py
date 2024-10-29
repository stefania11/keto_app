from openai import OpenAI
import os

# Set up the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload the training file
training_file = client.files.create(
    file=open("prepared_dataset.jsonl", "rb"),
    purpose="fine-tune"
)

# Create a fine-tuning job
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=training_file.id,
    model="gpt-4o-2024-08-06"
)

# Print the fine-tuning job details
print(f"Fine-tuning job created: {fine_tune_job}")
