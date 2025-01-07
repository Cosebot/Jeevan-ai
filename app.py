from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import random

# Initialize Flask app
app = Flask(__name__)

# English responses dictionary
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"],
    "i am fine": ["Good to hear!", "Great to know!", "Stay blessed!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            return random.choice(responses)
    return "Sorry, I didn't understand that."

# Function to generate speech using gTTS
@app.route('/speak', methods=['GET'])
def speak_text():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')
    tts = gTTS(text=text, lang=language)
    temp_mp3_path = "response.mp3"
    tts.save(temp_mp3_path)
    return send_file(temp_mp3_path, mimetype='audio/mpeg', as_attachment=False)

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Home route
@app.route('/')
def home():
    return render_template_string(html_template)

# HTML Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sanji AI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg-color, #000); color: var(--text-color, #fff); transition: all 0.3s ease; }
        .chat-container { display: flex; flex-direction: column; height: 100vh; }
        .chat-box { flex-grow: 1; padding: 10px; overflow-y: auto; background-color: var(--chat-bg, #111); display: flex; flex-direction: column-reverse; }
        .input-container { display: flex; padding: 10px; background-color: var(--chat-bg, #111); }
        #user-input { flex-grow: 1; padding: 10px; border: none; border-radius: 5px; background-color: #333; color: #fff; }
        button { margin-left: 10px; padding: 10px; background-color: #007bff; border: none; border-radius: 5px; color: #fff; cursor: pointer; }
        .message { margin: 5px 0; padding: 10px; border-radius: 10px; max-width: 70%; }
        .user { align-self: flex-end; background-color: #444; }
        .bot { align-self: flex-start; background-color: #555; }
        .hamburger-menu { position: fixed; left: 0; top: 0; width: 200px; height: 100vh; background-color: #222; display: none; flex-direction: column; }
        .menu-item { color: #fff; padding: 10px; border-bottom: 1px solid #444; cursor: pointer; }
        .menu-item:hover { background-color: #333; }
        #hamburger { position: fixed; left: 10px; top: 10px; cursor: pointer; color: #fff; font-size: 24px; }
        .theme-buttons { display: flex; flex-direction: column; margin: 10px; }
        .theme-buttons button { margin: 5px 0; }
    </style>
</head>
<body>
    <div id="hamburger">☰</div>
    <div class="hamburger-menu" id="menu">
        <div class="menu-item" onclick="window.location.reload()">Home</div>
        <div class="menu-item">Settings
            <div class="theme-buttons">
                <button onclick="setTheme('diamond')">Diamond</button>
                <button onclick="setTheme('sakura')">Sakura</button>
                <button onclick="setTheme('gold')">Gold</button>
                <button onclick="setTheme('cloud')">Cloud</button>
                <button onclick="setTheme('ant')">Ant</button>
            </div>
        </div>
        <div class="menu-item"><a href="mailto:hazanulashkar@gmail.com" style="color: inherit;">Contact Us</a></div>
    </div>
    <div class="chat-container">
        <div id="chat-box" class="chat-box"></div>
        <div class="input-container">
            <input id="user-input" type="text" placeholder="Type a message..." />
            <button id="send-btn">Send</button>
            <button id="voice-btn">🎤 Speak</button>
        </div>
    </div>

    <script>
        const themes = {
            diamond: { '--bg-color': 'lightblue', '--text-color': '#000', '--chat-bg': '#e0f7fa' },
            sakura: { '--bg-color': 'pink', '--text-color': '#000', '--chat-bg': '#ffebee' },
            gold: { '--bg-color': 'yellow', '--text-color': '#000', '--chat-bg': '#fff9c4' },
            cloud: { '--bg-color': '#fff', '--text-color': '#000', '--chat-bg': '#f1f1f1' },
            ant: { '--bg-color': '#000', '--text-color': '#fff', '--chat-bg': '#333' }
        };

        window.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme') || 'ant';
            setTheme(savedTheme);
        });

        const menu = document.getElementById('menu');
        document.getElementById('hamburger').addEventListener('click', () => {
            menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
        });

        function setTheme(theme) {
            const themeColors = themes[theme];
            for (const key in themeColors) {
                document.body.style.setProperty(key, themeColors[key]);
            }
            localStorage.setItem('theme', theme);
        }

        const chatBox = document.getElementById('chat-box');

        document.getElementById('send-btn').addEventListener('click', () => {
            const inputField = document.getElementById('user-input');
            const userMessage = inputField.value.trim();

            if (!userMessage) return;

            // Append user message to chat box
            const userDiv = document.createElement('div');
            userDiv.textContent = userMessage;
            userDiv.className = 'message user';
            chatBox.appendChild(userDiv);

            inputField.value = '';

            // Fetch bot response
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            })
            .then(res => res.json())
            .then(data => {
                const botDiv = document.createElement('div');
                botDiv.textContent = data.response;
                botDiv.className = 'message bot';
                chatBox.appendChild(botDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)