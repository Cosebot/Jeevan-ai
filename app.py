from flask import Flask, render_template_string, request, jsonify
import random
from gtts import gTTS
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
    "i am fine": ["Good to hear!", "Great man! ", " May god bless you!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # Check if the input is in English
    if any(word in user_input for word in english_responses.keys()):
        return random.choice(english_responses.get(user_input.lower(), ["Sorry, I didn't understand that."]))

    return "Sorry, I didn't understand that."

# Function to make the chatbot speak using gTTS (Google Text-to-Speech)
def speak(text, language="en"):
    tts = gTTS(text=text, lang=language)
    tts.save("response.mp3")  # Save the speech as an MP3 file
    os.system("start response.mp3")  # Play the speech on Windows, use 'afplay' on macOS or 'mpg321' on Linux

# HTML, CSS, and JavaScript embedded in the Python script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        /* Add the previous CSS styles here */
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
        </div>
    </div>
    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

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
                
                // Call TTS function to speak the response
                fetch(`/speak?text=${encodeURIComponent(data.response)}&language=${language}`);
            });
        });
    </script>
</body>
</html>
"""

# Route for the chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Route to generate TTS and play the response
@app.route('/speak', methods=['GET'])
def speak_text():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')
    speak(text, language)
    return jsonify({'status': 'speaking'})

# Route for the main page (HTML)
@app.route('/')
def home():
    return render_template_string(html_template)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)