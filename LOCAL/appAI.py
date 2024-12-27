import os
import datetime
from flask import Flask, render_template_string, request, jsonify, send_from_directory
import requests
from gradio_client import Client

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Gradio Client for the model (Image Generation)
client = Client("stabilityai/stable-diffusion")

# Directory to save images
image_dir = "images"  # This is the /images folder you want
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# HTML Template for the homepage (Select Service)
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Choose a Service</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
            background-color: #f4f4f9;
        }
        h1 {
            color: #333;
        }
        .button {
            padding: 15px 30px;
            font-size: 18px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 20px;
        }
        .button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>

    <h1>Welcome! Choose a Service</h1>
    <div>
        <a href="{{ url_for('summarization') }}">
            <button class="button">Text Summarization</button>
        </a>
        <a href="{{ url_for('image_generation') }}">
            <button class="button">Text-to-Image Generation</button>
        </a>
    </div>

</body>
</html>
"""

# HTML Template for Text Summarization Page
SUMMARIZATION_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text Summarization</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        textarea {
            width: 100%;
            height: 150px;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
        #result {
            background-color: #f4f4f4;
            padding: 10px;
        }
        #loader {
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 20px;
        }
        #loader:before {
            content: "Loading...";
            font-weight: bold;
            color: #007BFF;
        }
    </style>
</head>
<body>

    <h1>Text Summarization</h1>
    <label for="textInput">Enter text to summarize:</label>
    <textarea id="textInput" placeholder="Type your text here..."></textarea>

    <button onclick="summarizeText()">Summarize</button>

    <h2>Summarized Text</h2>
    <textarea id="result" readonly></textarea>

    <div id="loader"></div>

    <script>
        function summarizeText() {
            const inputText = document.getElementById("textInput").value;

            if (inputText.trim() === "") {
                alert("Please enter some text to summarize.");
                return;
            }

            document.getElementById("loader").style.display = "block";
            document.getElementById("result").value = "";  // Clear previous result

            fetch("/summarize", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: inputText
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("loader").style.display = "none";

                if (data.summary) {
                    document.getElementById("result").value = data.summary;
                } else {
                    alert("Error: " + (data.error || "Something went wrong."));
                }
            })
            .catch(error => {
                document.getElementById("loader").style.display = "none";
                console.error("Error summarizing text:", error);
                alert("Something went wrong. Please try again.");
            });
        }
    </script>

</body>
</html>
"""

# HTML Template for Text-to-Image Generation Page
IMAGE_GENERATION_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Text-to-Image Generation</title>
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
        <form method="POST" action="{{ url_for('image_generation') }}">
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
"""

# Route to the homepage
@app.route('/')
def home():
    return render_template_string(HOME_HTML)

# Route to the Text Summarization page
@app.route('/summarization', methods=['GET'])
def summarization():
    return render_template_string(SUMMARIZATION_HTML)

# Route to the Text-to-Image Generation page
@app.route('/image-generation', methods=['GET', 'POST'])
def image_generation():
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

    return render_template_string(IMAGE_GENERATION_HTML, image_filename=image_filename)

# Route to summarize text
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

# Custom route to serve images from the images directory
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(image_dir, filename)

if __name__ == '__main__':
    app.run(debug=True)
