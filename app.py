from flask import Flask, request, jsonify, send_file, render_template_string
from gtts import gTTS
import os
import random
import threading
import time
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import speedup

app = Flask(__name__)

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

@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot messages"""
    data = request.get_json()
    message = data.get("message", "")
    response_text = get_chatbot_response(message)
    return jsonify({"response": response_text})

@app.route("/speak", methods=["POST"])
def speak():
    """Converts chatbot response to speech and modulates the voice"""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)

    # Modulate Voice (Change Pitch & Speed)
    audio = AudioSegment.from_file(filename)
    audio = speedup(audio, playback_speed=1.2)  # Increase speed
    audio = audio + 6  # Increase pitch
    modulated_filename = "modulated_temp.mp3"
    audio.export(modulated_filename, format="mp3")

    # Cleanup after some time
    threading.Thread(target=cleanup_audio, args=(filename, modulated_filename)).start()

    return send_file(modulated_filename, mimetype="audio/mpeg")

def cleanup_audio(*files):
    """Deletes temp audio files after 10 seconds"""
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

@app.route("/speech", methods=["POST"])
def speech_to_text():
    """Converts speech input to text"""
    recognizer = sr.Recognizer()

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service is unavailable"}), 500

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
    <style>
        :root {
            --primary-color: #1b1f3b;
            --secondary-color: white;
            --text-color: black;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: var(--primary-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            justify-content: center;
            margin: 0;
        }

        #chat-box {
            width: 90%;
            max-width: 400px;
            height: 60vh;
            background-color: var(--secondary-color);
            border-radius: 10px;
            padding: 10px;
            overflow-y: auto;
            color: var(--text-color);
        }

        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            max-width: 80%;
        }

        .user {
            background-color: #e1f7d5;
            text-align: right;
        }

        .bot {
            background-color: #d8e3fc;
            text-align: left;
        }

        .chat-input {
            display: flex;
            align-items: center;
            background-color: white;
            border-radius: 30px;
            padding: 10px;
            width: 90%;
            max-width: 500px;
            margin-top: 10px;
        }

        #theme-btn {
            background: yellow;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>

    <button id="theme-btn">Change Theme</button>
    <div id="chat-box"></div>

    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        let themeIndex = 0;
        const themes = [
            { primary: '#ff006e', secondary: '#ffbe0b', text: '#000' },
            { primary: '#0d1b2a', secondary: '#00b4d8', text: '#fff' },
            { primary: '#1a3c40', secondary: '#4CAF50', text: '#fff' },
            { primary: '#ff0000', secondary: '#8a2be2', text: '#fff' }
        ];

        document.getElementById('theme-btn').addEventListener('click', () => {
            themeIndex = (themeIndex + 1) % themes.length;
            document.documentElement.style.setProperty('--primary-color', themes[themeIndex].primary);
            document.documentElement.style.setProperty('--secondary-color', themes[themeIndex].secondary);
            document.documentElement.style.setProperty('--text-color', themes[themeIndex].text);
        });

        function sendMessage() {
            const userInput = document.getElementById('user-input').value.trim();
            if (!userInput) return;

            const chatBox = document.getElementById('chat-box');
            chatBox.innerHTML += `<div class='message user'>${userInput}</div>`;
            
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput })
            })
            .then(response => response.json())
            .then(data => {
                chatBox.innerHTML += `<div class='message bot'>${data.response}</div>`;
            });

            document.getElementById('user-input').value = '';
        }
    </script>

</body>
</html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)