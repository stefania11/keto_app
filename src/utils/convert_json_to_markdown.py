import json

def convert_json_to_markdown(json_file, markdown_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    with open(markdown_file, 'w') as f:
        f.write("# Block Analysis Results\n\n")

        f.write("## Top Block Types\n\n")
        f.write("| Block Type | Count |\n")
        f.write("|------------|-------|\n")
        for block_type, count in sorted(data['block_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"| {block_type} | {count} |\n")

        f.write("\n## Top Project Structures\n\n")
        f.write("| Project Structure | Count |\n")
        f.write("|-------------------|-------|\n")
        for structure, count in sorted(data['project_structures'].items(), key=lambda x: int(x[1]), reverse=True)[:10]:
            f.write(f"| {structure} | {count} |\n")

if __name__ == "__main__":
    json_file = "block_analysis_results.json"
    markdown_file = "block_analysis_results.md"
    convert_json_to_markdown(json_file, markdown_file)
    print(f"Conversion complete. Results saved to {markdown_file}")
