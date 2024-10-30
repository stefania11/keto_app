import os
from openai import OpenAI

# Set up the OpenAI client
client = OpenAI()

# Fine-tuning job ID
job_id = "ftjob-hI8LMzIV2t1yUKyR7n2YmPmO"

try:
    # Retrieve the fine-tuning job
    job = client.fine_tuning.jobs.retrieve(job_id)

    # Print job details
    print(f"Job ID: {job.id}")
    print(f"Status: {job.status}")
    print(f"Model: {job.model}")
    print(f"Created at: {job.created_at}")
    print(f"Finished at: {job.finished_at}")

    if job.status == "succeeded":
        print(f"Fine-tuned model: {job.fine_tuned_model}")
    elif job.status == "failed":
        print(f"Error: {job.error}")
    else:
        print("Job is still in progress. Check back later for updates.")

except Exception as e:
    print(f"An error occurred: {str(e)}")

print("\nMonitor the job status using the OpenAI dashboard or API for more detailed information.")
