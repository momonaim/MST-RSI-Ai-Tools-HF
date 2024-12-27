import inspect
import os
import datetime

from flask import Flask, send_file, render_template, url_for, request, redirect
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from diffusers import StableDiffusionPipeline
from io import BytesIO
import base64

app = Flask(__name__)

# Load the Pegasus model and tokenizer for text summarization
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)

# Set device to CPU
device = "cpu"
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

print(inspect.getfile(PegasusForConditionalGeneration))
print(inspect.getfile(PegasusTokenizer))

# Initialize the Stable Diffusion pipeline for text-to-image
model_id = "CompVis/stable-diffusion-v1-4"  # Use a smaller model for better CPU performance
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)  # Use float32 for CPU
pipe = pipe.to(device)
pipe.enable_attention_slicing()  # Enable attention slicing to reduce memory usage and speed up generation

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/txt2image', methods=['GET','POST'])
def generate_image():
    image_url = None

    if request.method == 'POST':
        # Get the prompt from the form data
        prompt = request.form.get('prompt', 'a photo of an astronaut riding a horse on mars')

        # Use a smaller resolution for faster processing
        image = pipe(prompt, height=256, width=256).images[0]  # Lower resolution for faster generation

        # Create a folder 'images' if it doesn't exist
        if not os.path.exists('images'):
            os.makedirs('images')

        # Get the current timestamp to append to the filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"images/generated_image_{timestamp}.png"

        # Save the image to the images folder with the timestamp in the filename
        image.save(filename)

        # Optionally, you can still show the image in the UI by converting it to base64
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert the image to a base64-encoded string for embedding in HTML
        image_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        # Pass the base64 image data to the show_image route using a POST request
        return render_template('result.html', image_data=image_base64)

    return render_template('txt2image.html', image_url=image_url)

@app.route('/show_image', methods=['POST'])
def show_image():
    # Since we are using POST, we can handle the image display by receiving the image data from the form
    image_data = request.form.get('image_data')
    return render_template('result.html', image_data=image_data)

@app.route('/text-summarization', methods=["POST"])
def summarize():
    if request.method == "POST":
        inputtext = request.form["inputtext_"]

        input_text = "summarize: " + inputtext
        tokenized_text = tokenizer.encode(input_text, return_tensors='pt', max_length=512).to(device)
        summary_ = model.generate(tokenized_text, min_length=30, max_length=300)
        summary = tokenizer.decode(summary_[0], skip_special_tokens=True)

    return render_template("output.html", data={"summary": summary})

if __name__ == '__main__':
    # It allows you to execute code when the file runs as a script
    app.run()
