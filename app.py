import inspect
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
model_id = "sd-legacy/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)  # Use float32 for CPU
pipe = pipe.to(device)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/txt2image', methods=['GET', 'POST'])
def generate_image():
    image_url = None

    if request.method == 'POST':
        # Get the prompt from the form data
        prompt = request.form.get('prompt', 'a photo of an astronaut riding a horse on mars')

        # Run the image generation pipeline on the CPU
        image = pipe(prompt).images[0]

        # Save the image to an in-memory file
        img_io = BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert the image to a base64-encoded string for embedding in HTML
        image_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

        # Redirect to a new page to show the result, passing the image data as a parameter
        return redirect(url_for('show_image', image_data=image_base64))

    return render_template('txt2image.html', image_url=image_url)

@app.route('/show_image')
def show_image():
    # Get the image data from the query parameter
    image_data = request.args.get('image_data')
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
    app.run(debug=True)
