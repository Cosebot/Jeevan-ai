import os
import requests
import shutil
from flask import Flask, request, jsonify, send_file, render_template_string

app = Flask(__name__)

# Replace with your Hugging Face API token
HF_TOKEN = "hf_xxx"  # Your Hugging Face token

# Create a temp folder if it doesn't exist
TEMP_FOLDER = "temp_images"
os.makedirs(TEMP_FOLDER, exist_ok=True)

def delete_old_images():
    """Deletes old images to prevent storage issues."""
    if os.path.exists(TEMP_FOLDER):
        shutil.rmtree(TEMP_FOLDER)
        os.makedirs(TEMP_FOLDER, exist_ok=True)

@app.route('/')
def home():
    """Serve the Chat UI."""
    return render_template_string(CHAT_HTML)

@app.route('/generate', methods=['GET'])
def generate_image():
    """Generates an image using Hugging Face API."""
    prompt = request.args.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    response = requests.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        delete_old_images()  # Clean old images before saving new one
        image_path = os.path.join(TEMP_FOLDER, "generated.png")

        with open(image_path, "wb") as f:
            f.write(response.content)

        return jsonify({"message": "Image generated!", "image_url": f"/image/generated.png"})
    else:
        return jsonify({"error": "Failed to generate image"}), 500

@app.route('/image/<filename>', methods=['GET'])
def serve_image(filename):
    """Serves generated images in chat."""
    return send_file(os.path.join(TEMP_FOLDER, filename), mimetype='image/png')

CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI Chat</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        #chatbox { width: 60%; height: 400px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; margin: auto; }
        #userInput { width: 60%; padding: 5px; margin-top: 10px; }
        #sendBtn { padding: 5px; }
        img { max-width: 300px; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>Sanji AI Chat</h2>
    <div id="chatbox"></div>
    <input type="text" id="userInput" placeholder="Type your message here">
    <button id="sendBtn" onclick="sendMessage()">Send</button>

    <script>
        function sendMessage() {
            let input = document.getElementById("userInput").value;
            let chatbox = document.getElementById("chatbox");

            let userMessage = `<p><strong>You:</strong> ${input}</p>`;
            chatbox.innerHTML += userMessage;

            if (input.toLowerCase().includes("generate an image of")) {
                fetch(`/generate?prompt=${encodeURIComponent(input)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.image_url) {
                        let botMessage = `<p><strong>Sanji AI:</strong> Here is your image:</p>
                                          <img src="${data.image_url}" width="300px">`;
                        chatbox.innerHTML += botMessage;
                    } else {
                        chatbox.innerHTML += `<p><strong>Sanji AI:</strong> Error generating image.</p>`;
                    }
                });
            } else {
                chatbox.innerHTML += `<p><strong>Sanji AI:</strong> I didn't understand.</p>`;
            }

            document.getElementById("userInput").value = ""; // Clear input field
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)