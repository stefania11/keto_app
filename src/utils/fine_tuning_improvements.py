import os
import json
from openai import OpenAI
from datetime import datetime
import time

def create_improved_fine_tuning_job():
    try:
        client = OpenAI(
            api_key=os.environ['OAI_key'],
            organization=os.environ['OAI_organization_id']
        )

        print('Starting fine-tuning process...')

        # Read and improve training data format
        print('Reading training data...')
        with open('standardized_training_data.jsonl', 'r') as f:
            current_data = [json.loads(line) for line in f]

        # Format data with improved system prompts
        print('Formatting data with improved prompts...')
        improved_data = []
        for item in current_data:
            improved_item = {
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an AI assistant that understands Scratch projects and can describe their structure.\n\nFormat Rules:\n1. Start with exactly " blocks:" (note the leading space)\n2. List each sprite on a new line\n3. Each sprite line must start with "sprite: "\n4. No extra text or explanations'
                    },
                    {
                        'role': 'user',
                        'content': item['prompt']
                    },
                    {
                        'role': 'assistant',
                        'content': item['completion']
                    }
                ]
            }
            improved_data.append(improved_item)

        # Save improved training data
        print('Saving improved training data...')
        output_file = 'improved_training_data.jsonl'
        with open(output_file, 'w') as f:
            for item in improved_data:
                f.write(json.dumps(item) + '\n')

        # Upload with retry logic
        print('Uploading training file...')
        max_attempts = 3
        file_id = None

        for attempt in range(max_attempts):
            try:
                with open(output_file, 'rb') as f:
                    response = client.files.create(
                        file=f,
                        purpose='fine-tune'
                    )
                file_id = response.id
                print(f'File uploaded successfully. ID: {file_id}')
                break
            except Exception as e:
                print(f'Upload attempt {attempt + 1} failed: {str(e)}')
                if attempt < max_attempts - 1:
                    print('Retrying upload...')
                    time.sleep(5)
                else:
                    raise Exception('Failed to upload file after multiple attempts')

        # Verify file processing
        print('Waiting for file processing...')
        max_wait = 60  # Maximum wait time in seconds
        start_time = time.time()

        while True:
            try:
                file_status = client.files.retrieve(file_id)
                print(f'File status: {file_status.status}')

                if file_status.status == 'processed':
                    print('File processing complete')
                    break

                if time.time() - start_time > max_wait:
                    raise Exception('File processing timeout')

                time.sleep(5)
            except Exception as e:
                print(f'Error checking file status: {str(e)}')
                raise

        # Create fine-tuning jobs with improved parameters
        print('Creating fine-tuning jobs...')
        models = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18']
        successful_jobs = []

        for model in models:
            try:
                print(f'Creating job for model: {model}')
                job = client.fine_tuning.jobs.create(
                    training_file=file_id,
                    model=model,
                    hyperparameters={
                        'n_epochs': 5,
                        'learning_rate_multiplier': 1.6,
                        'batch_size': 4  # Added batch size parameter
                    }
                )
                successful_jobs.append({
                    'model': model,
                    'job_id': job.id,
                    'status': job.status,
                    'created_at': datetime.now().isoformat(),
                    'parameters': {
                        'n_epochs': 5,
                        'learning_rate_multiplier': 1.6,
                        'batch_size': 4
                    }
                })
                print(f'Job created successfully. ID: {job.id}')
                time.sleep(5)  # Wait between job creations
            except Exception as e:
                print(f'Error creating job for {model}: {str(e)}')

        # Save job information
        if successful_jobs:
            output_file = f'fine_tuning_jobs_{datetime.now().isoformat()}.json'
            with open(output_file, 'w') as f:
                json.dump(successful_jobs, f, indent=2)
            print(f'Job information saved to {output_file}')
        else:
            print('No successful jobs created')

    except Exception as e:
        print(f'Error in fine-tuning process: {str(e)}')
        raise

if __name__ == '__main__':
    try:
        print('Starting improved fine-tuning process...')
        create_improved_fine_tuning_job()
        print('Fine-tuning process completed successfully')
    except Exception as e:
        print(f'Fatal error: {str(e)}')
