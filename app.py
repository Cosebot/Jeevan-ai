from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import random
import os

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
    
    # Generate speech for the bot's response
    tts = gTTS(text=response, lang='en')
    audio_path = "static/response.mp3"
    tts.save(audio_path)

    return jsonify({'response': response, 'audio_path': audio_path})

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
        :root {
            --bg-color: #f0f0f0;
            --chat-bg-color: #fff;
            --user-msg-bg-color: #d1e7dd;
            --bot-msg-bg-color: #f8d7da;
            --btn-bg-color: #007bff;
            --btn-text-color: #fff;
        }
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: var(--bg-color);
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .chat-box {
            flex-grow: 1;
            padding: 10px;
            overflow-y: auto;
        }
        .input-container {
            display: flex;
            padding: 10px;
            background-color: var(--chat-bg-color);
        }
        #user-input {
            flex-grow: 1;
            padding: 10px;
            border: none;
            border-radius: 5px;
            background-color: #ddd;
            color: #333;
        }
        button {
            padding: 10px;
            background-color: var(--btn-bg-color);
            border: none;
            border-radius: 5px;
            color: var(--btn-text-color);
            cursor: pointer;
        }
        .message {
            margin: 5px 0;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user {
            align-self: flex-end;
            background-color: var(--user-msg-bg-color);
        }
        .bot {
            align-self: flex-start;
            background-color: var(--bot-msg-bg-color);
        }

        /* Theme styles */
        .theme-buttons {
            display: flex;
            flex-direction: column;
            margin-top: 10px;
        }
        .theme-buttons button {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div id="chat-box" class="chat-box"></div>
        <div class="input-container">
            <input id="user-input" type="text" placeholder="Type a message..." />
            <button id="send-btn">Send</button>
            <button id="voice-btn">🎤 Speak</button>
        </div>
        <div class="theme-buttons">
            <button onclick="setTheme('diamond')">Diamond</button>
            <button onclick="setTheme('pink')">Pink</button>
            <button onclick="setTheme('gold')">Gold</button>
            <button onclick="setTheme('white')">White</button>
            <button onclick="setTheme('black')">Black</button>
        </div>
    </div>

    <script>
        const themes = {
            diamond: { '--bg-color': '#D1F7FF', '--chat-bg-color': '#E5FFFF', '--user-msg-bg-color': '#B6E3F1', '--bot-msg-bg-color': '#A2E0FB' },
            pink: { '--bg-color': '#F8E0E6', '--chat-bg-color': '#F8C6D7', '--user-msg-bg-color': '#F1A0B5', '--bot-msg-bg-color': '#F49EC2' },
            gold: { '--bg-color': '#FFD700', '--chat-bg-color': '#FFEC99', '--user-msg-bg-color': '#FFB84D', '--bot-msg-bg-color': '#F5C24A' },
            white: { '--bg-color': '#FFFFFF', '--chat-bg-color': '#F9F9F9', '--user-msg-bg-color': '#D3D3D3', '--bot-msg-bg-color': '#E0E0E0' },
            black: { '--bg-color': '#2E2E2E', '--chat-bg-color': '#444444', '--user-msg-bg-color': '#555555', '--bot-msg-bg-color': '#666666' }
        };

        function setTheme(theme) {
            const themeColors = themes[theme];
            for (const key in themeColors) {
                document.body.style.setProperty(key, themeColors[key]);
            }
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

                // Play the bot's voice response
                const audio = new Audio(data.audio_path);
                audio.play();

                chatBox.scrollTop = chatBox.scrollHeight;
            });
        });

        // Voice input using Speech Recognition API
        const voiceBtn = document.getElementById('voice-btn');
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        
        recognition.onresult = function(event) {
            const userMessage = event.results[0][0].transcript;
            document.getElementById('user-input').value = userMessage;

            // Automatically send the message after voice input
            document.getElementById('send-btn').click();
        }

        voiceBtn.addEventListener('click', () => {
            recognition.start();
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)