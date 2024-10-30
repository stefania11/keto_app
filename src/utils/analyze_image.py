import os
import openai
from openai import OpenAI
import sys
import base64

# Set up the OpenAI client
client = OpenAI()

# Set the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fine-tuned model name
model_name = "gpt-4o"  # Changed to use the model from the example

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze these Scratch blocks and provide programming advice:"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Please provide an image path as an argument.")
        sys.exit(1)

    # Analyze the image using the OpenAI API
    analysis = analyze_image(image_path)

    print("\nAPI Response for Scratch Block Analysis:")
    print(analysis)
