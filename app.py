from flask import Flask, request, jsonify, send_file, render_template_string
import os
from gtts import gTTS

app = Flask(__name__)

# Ensure a temp directory exists for saving audio
TEMP_DIR = "static"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# Chatbot logic
def chatbot_response(user_input):
    responses = {
        "hello": "Hi there!",
        "how are you": "I'm just a bot, but I'm doing fine!",
        "what's your name": "I'm Sanji AI, your assistant.",
        "bye": "Goodbye! Have a great day!",
        "default": "I'm still learning! Can you rephrase that?"
    }
    return responses.get(user_input.lower(), responses["default"])

# Serve frontend (HTML)
@app.route('/')
def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sanji AI</title>
        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        <style>
            /* Default Theme */
            :root {
                --primary-color: #1b1f3b;
                --secondary-color: #ffffff;
            }
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
                background-color: var(--primary-color);
                color: var(--secondary-color);
                justify-content: center;
                margin: 0;
                width: 100vw;
                max-width: 430px;
            }
            #chat-box {
                width: 95%;
                max-width: 400px;
                height: 70vh;
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                overflow-y: auto;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                color: black;
            }
            .message {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                max-width: 80%;
            }
            .user {
                background-color: #e1f7d5;
                align-self: flex-end;
                text-align: right;
            }
            .bot {
                background-color: #d8e3fc;
                align-self: flex-start;
                text-align: left;
            }
            .chat-input {
                display: flex;
                align-items: center;
                background-color: white;
                border-radius: 30px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                width: 90%;
                max-width: 500px;
                margin-top: 10px;
                position: relative;
            }
            .icon-container {
                display: flex;
                justify-content: space-around;
                width: 100%;
                margin-top: 10px;
            }
            .icon-group {
                display: flex;
                flex-direction: column;
                align-items: center;
                font-size: 14px;
                cursor: pointer;
                background: #001F3F;
                color: white;
                padding: 12px;
                border-radius: 50px;
                width: 55px;
                height: 55px;
                display: flex;
                justify-content: center;
            }
            .icon-group i {
                color: white;
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <button class="settings-btn" id="settings-btn">⚙️</button>
        <div id="chat-box"></div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Message">
        </div>
        <div class="icon-container">
            <div class="icon-group" id="voice-btn">
                <i class="fas fa-microphone"></i>
                <span>Mic</span>
            </div>
            <div class="icon-group" id="send-btn">
                <i class="fas fa-paper-plane"></i>
                <span>Send</span>
            </div>
        </div>
        <script>
            document.getElementById('send-btn').addEventListener('click', () => {
                const message = document.getElementById('user-input').value.trim();
                if (!message) return;
                const chatBox = document.getElementById('chat-box');
                const messageDiv = document.createElement('div');
                messageDiv.textContent = message;
                messageDiv.className = "message user";
                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
                document.getElementById('user-input').value = '';
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

# Handle chat requests and generate TTS response
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = chatbot_response(user_message)

    # Generate and save TTS audio
    tts_file = os.path.join(TEMP_DIR, "response.mp3")
    tts = gTTS(bot_reply, lang='en')
    tts.save(tts_file)

    return jsonify({"reply": bot_reply, "audio": "/" + tts_file})

# Serve the generated TTS file
@app.route('/static/response.mp3')
def get_audio():
    return send_file("static/response.mp3", mimetype="audio/mp3")

if __name__ == '__main__':
    app.run(debug=True)