import os
import datetime
from flask import Flask, render_template_string, request, send_from_directory
from gradio_client import Client

app = Flask(__name__)

# Initialize the Gradio Client for the model
client = Client("stabilityai/stable-diffusion")

# Directory to save images
image_dir = "images"  # This is the /images folder you want
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# HTML template as a string (for home page)
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text to Image</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            text-align: center;
            height: 100vh;
            margin: 0;
            background-color: #f4f4f9;
            overflow-y: auto;
        }

        h1 {
            color: #333;
        }
        textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            resize: vertical;
        }
        input[type="submit"] {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
        img {
            max-width: 100%;
            max-height: 500px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Generate an Image from Text</h1>
        <form method="POST" action="{{ url_for('home') }}">
            <label for="prompt">Enter a prompt for the image:</label><br>
            <textarea id="prompt" name="prompt" rows="4" cols="50" required>{{ request.form.get('prompt') }}</textarea><br><br>
            <input type="submit" value="Generate Image">
        </form>

        {% if image_filename %}
            <h2>Generated Image:</h2>
            <img src="{{ url_for('serve_image', filename=image_filename) }}" alt="Generated Image">
        {% endif %}
    </div>
</body>
</html>
'''

# Custom route to serve images from the images directory
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(image_dir, filename)

@app.route('/', methods=['GET', 'POST'])
def home():
    image_filename = None  # Initialize to None in case there is no image to display

    if request.method == 'POST':
        prompt = request.form.get('prompt', 'a photo of an astronaut riding a horse on mars')

        # Use the Gradio client to generate an image based on the provided prompt
        result = client.predict(
            prompt=prompt,
            negative="",
            scale=9,  # Adjust scale value as needed
            api_name="/infer"
        )

        print(f"Gradio Result: {result}")  # Debug the response from Gradio

        # Extract the file path from the result
        if isinstance(result, list) and len(result) > 0:
            image_path = result[0].get('image')

            # Ensure the image path exists
            if os.path.exists(image_path):
                # Save the image with a timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_filename = f"generated_image_{timestamp}.jpg"
                saved_image_path = os.path.join(image_dir, image_filename)

                # Copy the image to the /images directory
                with open(image_path, "rb") as image_file:
                    with open(saved_image_path, "wb") as output_file:
                        output_file.write(image_file.read())

    return render_template_string(html_template, image_filename=image_filename)

if __name__ == '__main__':
    app.run(debug=True)
