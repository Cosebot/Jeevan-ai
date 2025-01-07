from flask import Flask, render_template_string, request, jsonify
from gtts import gTTS
import random
import os

app = Flask(__name__)

# Sample chatbot responses
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"],
    "i am fine": ["Good to hear!", "Great to know!", "Stay blessed!"]
}

# Function to get chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            return random.choice(responses)
    return "Sorry, I didn't understand that."

# HTML Template with themes
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sanji AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f1f1f1;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        #chat-box {
            width: 100%;
            max-width: 500px;
            height: 400px;
            background-color: #fff;
            border: 1px solid #ccc;
            padding: 20px;
            overflow-y: auto;
            border-radius: 10px;
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
        }
        .bot {
            background-color: #d8e3fc;
            align-self: flex-start;
        }
        .input-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 10px;
        }
        #user-input {
            padding: 10px;
            font-size: 16px;
            border-radius: 5px;
            border: 1px solid #ccc;
            width: 70%;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }

        /* Theme styles */
        body.diamond {
            background-color: #b9e0e6;
        }
        body.pink {
            background-color: #ffc0cb;
        }
        body.gold {
            background-color: #ffd700;
        }
        body.white {
            background-color: #ffffff;
        }
        body.black {
            background-color: #1a1a1a;
            color: white;
        }
    </style>
</head>
<body>
    <div id="chat-box"></div>
    <div class="input-container">
        <input id="user-input" type="text" placeholder="Type a message..." />
        <button id="send-btn">Send</button>
        <button id="voice-btn">🎤 Speak</button>
    </div>

    <!-- Theme Selector -->
    <div style="text-align: center; margin-top: 20px;">
        <button onclick="changeTheme('diamond')">Diamond Theme</button>
        <button onclick="changeTheme('pink')">Pink Theme</button>
        <button onclick="changeTheme('gold')">Gold Theme</button>
        <button onclick="changeTheme('white')">White Theme</button>
        <button onclick="changeTheme('black')">Black Theme</button>
    </div>

    <script>
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
                const audio = new Audio('data:audio/mpeg;base64,' + data.audio);
                audio.play();

                chatBox.scrollTop = chatBox.scrollHeight;
            });
        });

        // Voice input functionality
        document.getElementById('voice-btn').addEventListener('click', () => {
            if (window.SpeechRecognition || window.webkitSpeechRecognition) {
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = 'en-US';
                recognition.start();

                recognition.onresult = function(event) {
                    const spokenText = event.results[0][0].transcript;
                    const inputField = document.getElementById('user-input');
                    inputField.value = spokenText;
                    document.getElementById('send-btn').click();
                };
                
                recognition.onerror = function(event) {
                    console.error("Error with speech recognition:", event.error);
                };
            } else {
                alert("Speech recognition is not supported in your browser.");
            }
        });

        function changeTheme(theme) {
            document.body.className = theme;
        }
    </script>
</body>
</html>
"""

# Home route
@app.route('/')
def home():
    return render_template_string(html_template)

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = get_chatbot_response(user_input)
    
    # Generate speech for bot response
    tts = gTTS(text=response, lang='en')
    audio_path = "response.mp3"
    tts.save(audio_path)
    
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    
    # Clean up
    os.remove(audio_path)
    
    return jsonify({'response': response, 'audio': audio_data.decode('base64')})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)