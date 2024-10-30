import json

def transform_json():
    with open('sampled_projects.json', 'r') as f:
        data = json.load(f)

    transformed_data = []
    for entry in data:
        project_id = entry['project_id']
        # Get the first block's name, which represents the sprite
        sprite_name = entry['blocks'][0]['name']

        transformed_entry = {
            'prompt': f'Describe Scratch project ID {project_id}.',
            'completion': f' blocks:\nsprite: {sprite_name}'
        }
        transformed_data.append(transformed_entry)

    with open('sampled_projects.json', 'w') as f:
        json.dump(transformed_data, f, indent=2)

if __name__ == '__main__':
    transform_json()
