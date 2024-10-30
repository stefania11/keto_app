import pandas as pd
import json

# Specify column names
column_names = ['project_id', 'block_id', 'sprite_id', 'type', 'name', 'x', 'y', 'z']

# Load the scripts.csv file with specified column names and handle variable field counts
df = pd.read_csv('scripts.csv', names=column_names, on_bad_lines='skip')

# Sample 1000 projects
sampled_df = df.sample(n=1000, random_state=42)

# Save the sampled projects to a new CSV file
sampled_df.to_csv('sampled_projects.csv', index=False)

# Convert sampled data to JSON format
json_data = []
for project_id, group in sampled_df.groupby('project_id'):
    project = {
        'project_id': int(project_id),
        'blocks': []
    }
    for _, row in group.iterrows():
        block = {
            'block_id': row['block_id'],
            'sprite_id': row['sprite_id'],
            'type': row['type'],
            'name': row['name'],
            'x': row['x'],
            'y': row['y'],
            'z': row['z']
        }
        project['blocks'].append(block)
    json_data.append(project)

# Save the JSON data to a file
with open('sampled_projects.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"Sampled {len(json_data)} projects and saved to sampled_projects.json")
