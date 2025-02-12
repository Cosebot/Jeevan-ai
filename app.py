from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from gtts import gTTS
import random
import os
import base64

app = Flask(__name__)
CORS(app)

# Chatbot Responses
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"],
    "i am fine": ["Good to hear!", "Great to know!", "Stay blessed!"]
}

def get_chatbot_response(user_input: str) -> str:
    """Simple chatbot logic"""
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            return random.choice(responses)
    return "Sorry, I didn't understand that."

def generate_tts(text: str) -> str:
    """Generate TTS and return base64"""
    tts = gTTS(text=text, lang='en')
    audio_path = "response.mp3"
    tts.save(audio_path)

    with open(audio_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    os.remove(audio_path)
    return audio_data

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot messages"""
    data = request.get_json()
    message = data.get("message", "")
    response_text = get_chatbot_response(message)
    audio_base64 = generate_tts(response_text)
    return jsonify({"response": response_text, "audio": audio_base64})

@app.route("/")
def serve_frontend():
    """Serves the chatbot UI"""
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
        }

        #chat-box {
            width: 90%;
            max-width: 500px;
            height: 400px;
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

        /* Settings Button */
        .settings-btn {
            background: yellow;
            border: none;
            cursor: pointer;
            font-size: 20px;
            padding: 10px;
            border-radius: 50%;
            position: absolute;
            top: 10px;
            right: 10px;
        }

        /* Dropdown Menu */
        .dropdown {
            position: absolute;
            top: 50px;
            right: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            display: none;
            padding: 10px;
        }

        .dropdown button {
            background: #1b1f3b;
            color: white;
            border: none;
            padding: 10px;
            cursor: pointer;
            width: 100%;
            text-align: left;
        }

        .dropdown button:hover {
            background: #2a315a;
        }

    </style>
</head>
<body>

    <button class="settings-btn" id="settings-btn">⚙️</button>

    <div class="dropdown" id="dropdown-menu">
        <button id="theme-btn">Change Theme</button>
    </div>

    <div id="chat-box"></div>
    
    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Message">
    </div>

    <div class="icon-container">
        <div class="icon-group" id="add-btn">
            <i class="fas fa-plus chat-icon"></i>
            <span>Add</span>
        </div>
        <div class="icon-group" id="search-btn">
            <i class="fas fa-globe chat-icon"></i>
            <span>Search</span>
        </div>
        <div class="icon-group" id="reason-btn">
            <i class="fas fa-lightbulb chat-icon"></i>
            <span>Reason</span>
        </div>
        <div class="icon-group" id="voice-btn">
            <i class="fas fa-microphone chat-icon"></i>
            <span>Mic</span>
        </div>
        <div class="icon-group" id="send-btn">
            <i class="fas fa-paper-plane chat-icon"></i>
            <span>Send</span>
        </div>
    </div>

    <script>
        let themeIndex = 0;

        const themes = [
            { primary: '#0d1b2a', secondary: '#00b4d8' },  // Cyber Glow
            { primary: '#1a3c40', secondary: '#4CAF50' },  // Toxic Slime
            { primary: '#ff006e', secondary: '#ffbe0b' },  // Retro Wave
            { primary: '#ff0000', secondary: '#8a2be2' },  // Laser Beam
            { primary: '#00a6fb', secondary: '#f72585' },  // Aqua Surge
            { primary: '#001f54', secondary: '#00ffff' },  // Midnight Pulse
            { primary: '#ff4500', secondary: '#ffd700' },  // Inferno Flash
            { primary: '#6a0dad', secondary: '#00ffff' }   // Glitch Effect
        ];

        document.getElementById('theme-btn').addEventListener('click', () => {
            themeIndex = (themeIndex + 1) % themes.length;
            document.documentElement.style.setProperty('--primary-color', themes[themeIndex].primary);
            document.documentElement.style.setProperty('--secondary-color', themes[themeIndex].secondary);
        });

        document.getElementById('settings-btn').addEventListener('click', () => {
            const dropdown = document.getElementById('dropdown-menu');
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });

        document.getElementById('voice-btn').addEventListener('click', () => {
            if (window.SpeechRecognition || window.webkitSpeechRecognition) {
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-US';
                recognition.start();

                recognition.onresult = function(event) {
                    const spokenText = event.results[0][0].transcript;
                    document.getElementById('user-input').value = spokenText;
                };
            } else {
                alert("Speech recognition not supported.");
            }
        });

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

if __name__ == "__main__":
    app.run(debug=True)