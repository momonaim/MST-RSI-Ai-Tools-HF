from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# HTML Template with embedded JavaScript, CSS, and a loading spinner
HTML_TEMPLATE = """
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

            // Show the loader
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
                // Hide the loader
                document.getElementById("loader").style.display = "none";

                if (data.summary) {
                    document.getElementById("result").value = data.summary;
                } else {
                    alert("Error: " + (data.error || "Something went wrong."));
                }
            })
            .catch(error => {
                // Hide the loader and display error
                document.getElementById("loader").style.display = "none";
                console.error("Error summarizing text:", error);
                alert("Something went wrong. Please try again.");
            });
        }
    </script>

</body>
</html>
"""


# Route to render the HTML page
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


# Route to handle text summarization
@app.route('/summarize', methods=['POST'])
def summarize():
    # Get the text input from the frontend
    input_text = request.json.get('text', '')

    if not input_text:
        return jsonify({'error': 'No text provided'}), 400

    # Call the Hugging Face API for summarization
    response = requests.post("https://pragnakalp-text-summarization.hf.space/run/predict", json={
        "data": ["T5 Abstractive Text Summarization", input_text]
    }).json()
    #BART Extractive Text Summarization

    summarized_text = response.get('data', [None])[0]

    if summarized_text:
        return jsonify({'summary': summarized_text})
    else:
        return jsonify({'error': 'Error in summarizing text'}), 500


if __name__ == '__main__':
    app.run(debug=True)
