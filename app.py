from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import os
import platform
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
    "i am fine": ["Good to hear!", "Great man! ", " May god bless you!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()

    if any(word in user_input for word in english_responses.keys()):
        return random.choice(english_responses.get(user_input.lower(), ["Sorry, I didn't understand that."]))

    return "Sorry, I didn't understand that."

# Function to make the chatbot speak using gTTS (Google Text-to-Speech)
def speak(text, language="en"):
    # Generate speech with Google TTS
    tts = gTTS(text=text, lang=language)
    tts.save("response.mp3")  # Save the speech as an MP3 file

    # Platform-specific commands to play the MP3 file
    current_platform = platform.system().lower()

    if current_platform == "windows":
        os.system("start response.mp3")  # Windows command
    elif current_platform == "darwin":  # macOS
        os.system("afplay response.mp3")  # macOS command
    elif current_platform == "linux" or current_platform == "linux2":
        os.system("mpg321 response.mp3")  # Linux command (ensure mpg321 is installed)
    else:
        print("Platform not supported for automatic audio playback.")

# Route for the chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Route to serve the audio file to the client for playback
@app.route('/speak', methods=['GET'])
def speak_text():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')
    tts = gTTS(text=text, lang=language)
    
    # Save the MP3 in a temporary file
    temp_mp3_path = "response.mp3"
    tts.save(temp_mp3_path)
    
    # Serve the MP3 file as a response
    return send_file(temp_mp3_path, mimetype='audio/mpeg', as_attachment=False)

# HTML, CSS, and JavaScript embedded in the Python script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        .chat-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            background-color: #f0f0f0;
        }
        .chat-box {
            flex-grow: 1;
            padding: 10px;
            overflow-y: scroll;
            max-height: 80%;
            background-color: white;
        }
        .input-container {
            display: flex;
            padding: 10px;
            background-color: #fff;
        }
        #user-input {
            flex-grow: 1;
            padding: 10px;
            border-radius: 5px;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 10px;
            margin-left: 10px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        .message {
            margin: 5px 0;
            padding: 5px 10px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user {
            background-color: #cfe2f3;
            align-self: flex-end;
        }
        .bot {
            background-color: #e9ecef;
            align-self: flex-start;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div id="chat-box" class="chat-box">
            <!-- Chat messages will appear here -->
        </div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your message here..." />
            <button id="send-btn">Send</button>
            <button id="voice-btn">🎤 Speak</button>
        </div>
    </div>
    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const voiceBtn = document.getElementById('voice-btn');

        sendBtn.addEventListener('click', () => {
            const userMessage = userInput.value;
            if (!userMessage.trim()) return;

            // Display user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'message user';
            userMessageDiv.textContent = userMessage;
            chatBox.appendChild(userMessageDiv);

            // Clear input field
            userInput.value = '';

            // Send message to Flask backend for response
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                // Display chatbot response
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot';
                botMessageDiv.textContent = data.response;
                chatBox.appendChild(botMessageDiv);
                
                // Trigger TTS to speak the response
                let language = "en";  // Default to English
                fetch(`/speak?text=${encodeURIComponent(data.response)}&language=${language}`)
                .then(response => response.blob())
                .then(blob => {
                    const audio = new Audio(URL.createObjectURL(blob));
                    audio.play();
                });
            });
        });

        voiceBtn.addEventListener('click', () => {
            // Start listening to user's voice input using the Web Speech API
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';  // Set the language for recognition
            recognition.start();

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript;
                sendBtn.click();  // Automatically send the voice input
            };

            recognition.onerror = (event) => {
                console.log('Speech recognition error:', event.error);
            };
        });
    </script>
</body>
</html>
"""

# Route for the main page (HTML)
@app.route('/')
def home():
    return render_template_string(html_template)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)