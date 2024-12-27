import os
import datetime
from flask import Flask, request, jsonify, send_from_directory
import requests
from gradio_client import Client

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Gradio Client for the model (Image Generation)
client = Client("stabilityai/stable-diffusion")

# Directory to save images
image_dir = "images"  # Use absolute path for Docker container
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(image_dir, filename)


@app.route('/summarize', methods=['POST'])
def summarize():
    input_text = request.json.get('text', '')

    if not input_text:
        return jsonify({'error': 'No text provided'}), 400

    # Call the Hugging Face API for summarization
    response = requests.post("https://pragnakalp-text-summarization.hf.space/run/predict", json={
        "data": ["T5 Abstractive Text Summarization", input_text]
    }).json()

    summarized_text = response.get('data', [None])[0]

    if summarized_text:
        return jsonify({'summary': summarized_text})
    else:
        return jsonify({'error': 'Error in summarizing text'}), 500

@app.route('/image-generation', methods=['POST'])
def image_generation():
    prompt = request.json.get('prompt', 'a photo of an astronaut riding a horse on mars')

    # Use the Gradio client to generate an image based on the provided prompt
    result = client.predict(
        prompt=prompt,
        negative="",
        scale=9,
        api_name="/infer"
    )

    if isinstance(result, list) and len(result) > 0:
        image_path = result[0].get('image')
        
        if os.path.exists(image_path):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            image_filename = f"generated_image_{timestamp}.jpg"
            saved_image_path = os.path.join(image_dir, image_filename)

            # Save the image to the /images folder
            with open(image_path, "rb") as image_file:
                with open(saved_image_path, "wb") as output_file:
                    output_file.write(image_file.read())
            return jsonify({"image_filename": f"/images/{image_filename}"})
        
    return jsonify({"error": "Failed to generate image"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
