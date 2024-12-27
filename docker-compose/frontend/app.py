from flask import Flask, render_template, request, jsonify
import requests

# Initialize the Flask app
app = Flask(__name__)

# Backend URL (Assuming backend is running on localhost:5001 in Docker)
BACKEND_URL = "http://backend:5000"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarization', methods=['GET'])
def summarization():
    return render_template('summarization.html')

@app.route('/image-generation', methods=['GET', 'POST'])
def image_generation():
    image_filename = None
    if request.method == 'POST':
        prompt = request.form.get('prompt', 'a photo of an astronaut riding a horse on mars')
        response = requests.post(f"{BACKEND_URL}/image-generation", json={"prompt": prompt})
        
        if response.status_code == 200:
            data = response.json()
            image_filename = data.get('image_url')
    
    return render_template('image_generation.html', image_filename=image_filename)

@app.route('/summarize', methods=['POST'])
def summarize():
    input_text = request.json.get('text', '')

    if not input_text:
        return jsonify({'error': 'No text provided'}), 400

    response = requests.post(f"{BACKEND_URL}/summarize", json={"text": input_text}).json()
    
    if 'summary' in response:
        return jsonify({'summary': response['summary']})
    else:
        return jsonify({'error': 'Error in summarizing text'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
