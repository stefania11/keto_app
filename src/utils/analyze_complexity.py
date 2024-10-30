import json
from collections import Counter
import heapq

def calculate_project_complexity(project):
    # Initialize complexity score
    complexity = 0

    # Get all blocks
    blocks = project.get('blocks', [])
    num_blocks = len(blocks)

    # Count number of blocks (base weight)
    complexity += num_blocks * 1.5

    # Analyze block types and their sophistication
    block_types = Counter(block.get('type', '') for block in blocks)

    # Define block categories and their weights
    block_weights = {
        # Control structures (high complexity)
        'control_if': 8,
        'control_if_else': 10,
        'control_repeat': 6,
        'control_repeat_until': 8,
        'control_forever': 5,
        'control_wait_until': 7,

        # Events and sensing (medium-high complexity)
        'event_broadcast': 6,
        'event_whenbroadcastreceived': 6,
        'sensing_touchingobject': 5,
        'sensing_keypressed': 4,
        'sensing_mousedown': 4,

        # Operations and variables (medium complexity)
        'operator_and': 4,
        'operator_or': 4,
        'operator_not': 4,
        'operator_random': 3,
        'data_variable': 4,
        'data_list': 5,
        'data_setvariableto': 3,

        # Motion and looks (basic complexity)
        'motion_movesteps': 2,
        'motion_gotoxy': 3,
        'motion_turnright': 2,
        'looks_switchcostumeto': 2,
        'looks_changesizeby': 2
    }

    # Calculate complexity based on block types and their weights
    for block_type, count in block_types.items():
        weight = block_weights.get(block_type, 1)  # Default weight of 1 for unknown blocks
        complexity += count * weight

    # Analyze sprite interactions and stage
    sprites = set()
    stage_blocks = 0
    custom_blocks = 0
    broadcasts = set()
    variables = set()
    lists = set()

    for block in blocks:
        # Count unique sprites
        sprite_name = block.get('name', '')
        sprites.add(sprite_name)

        # Count stage-specific blocks
        if sprite_name.lower() == 'stage':
            stage_blocks += 1

        # Count custom blocks
        if block.get('type', '').startswith('procedures_'):
            custom_blocks += 1

        # Track broadcast messages
        if block.get('type', '').startswith('event_'):
            if 'fields' in block and 'BROADCAST_OPTION' in block['fields']:
                broadcasts.add(block['fields']['BROADCAST_OPTION'])

        # Track variables and lists
        if block.get('type', '').startswith('data_'):
            if 'fields' in block:
                if 'VARIABLE' in block['fields']:
                    variables.add(block['fields']['VARIABLE'])
                if 'LIST' in block['fields']:
                    lists.add(block['fields']['LIST'])

    # Add complexity for various interaction elements
    complexity += len(sprites) * 5  # Sprite variety
    complexity += stage_blocks * 3  # Stage interaction
    complexity += custom_blocks * 8  # Custom block definitions
    complexity += len(broadcasts) * 6  # Broadcast messages
    complexity += len(variables) * 4  # Variable usage
    complexity += len(lists) * 5  # List usage

    # Bonus for projects with multiple types of interactions
    interaction_types = sum([
        bool(stage_blocks),
        bool(custom_blocks),
        bool(broadcasts),
        bool(variables),
        bool(lists),
        len(sprites) > 1
    ])
    complexity += interaction_types * 10  # Bonus for diverse interaction types

    return {
        'project_id': project.get('project_id'),
        'complexity_score': int(complexity),
        'num_blocks': num_blocks,
        'num_sprites': len(sprites),
        'num_custom_blocks': custom_blocks,
        'num_broadcasts': len(broadcasts),
        'num_variables': len(variables),
        'num_lists': len(lists),
        'block_types': dict(block_types),
        'has_stage_interaction': bool(stage_blocks),
        'interaction_types': interaction_types
    }

def analyze_projects():
    try:
        # Read the original JSON file
        with open('sampled_projects.json', 'r') as f:
            data = json.load(f)

        # Calculate complexity for each project
        project_complexities = []
        for project in data:
            if isinstance(project, dict) and 'blocks' in project:
                complexity_info = calculate_project_complexity(project)
                project_complexities.append(complexity_info)

        # Sort projects by complexity score
        project_complexities.sort(key=lambda x: x['complexity_score'], reverse=True)

        # Save analysis results
        with open('project_complexity_analysis.json', 'w') as f:
            json.dump({
                'total_projects': len(project_complexities),
                'projects': project_complexities
            }, f, indent=2)

        # Print summary of top 10 most complex projects
        print("\nTop 10 Most Complex Projects:")
        for i, proj in enumerate(project_complexities[:10], 1):
            print(f"\n{i}. Project ID: {proj['project_id']}")
            print(f"   Complexity Score: {proj['complexity_score']}")
            print(f"   Number of Blocks: {proj['num_blocks']}")
            print(f"   Number of Sprites: {proj['num_sprites']}")
            print(f"   Custom Blocks: {proj['num_custom_blocks']}")
            print(f"   Broadcasts: {proj['num_broadcasts']}")
            print(f"   Variables: {proj['num_variables']}")
            print(f"   Lists: {proj['num_lists']}")
            print(f"   Has Stage Interaction: {proj['has_stage_interaction']}")
            print(f"   Interaction Types: {proj['interaction_types']}/6")

        return project_complexities

    except Exception as e:
        print(f"Error analyzing projects: {str(e)}")
        return None

if __name__ == '__main__':
    analyze_projects()
