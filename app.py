from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import random
import os
import requests

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

# Google Search API Key and Engine ID
API_KEY = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"
SEARCH_ENGINE_ID = "915e7f3b9d9d245ff"

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            return random.choice(responses)
    return "Sorry, I didn't understand that."

# Function to fetch search results using Google API
def fetch_search_results(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "items" in data:
            top_result = data["items"][0]
            return f"Result: {top_result['title']}\nLink: {top_result['link']}"
        else:
            return "No results found."
    else:
        return "Error fetching search results. Please try again later."

# Generate speech response
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
    is_query_mode = request.json.get('query_mode', False)
    
    if is_query_mode:
        response = fetch_search_results(user_input)
    else:
        response = get_chatbot_response(user_input)
    
    # Generate speech for the response
    tts = gTTS(text=response, lang='en')
    audio_path = "static/response.mp3"
    tts.save(audio_path)

    return jsonify({'response': response, 'audio_path': audio_path})

# HTML Template with Themes
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot with Themes</title>
    <style>
        :root {
            --background-color: #000;
            --text-color: #fff;
            --button-color: #007bff;
            --user-message-color: #444;
            --bot-message-color: #555;
        }

        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--background-color); color: var(--text-color); }
        .chat-container { display: flex; flex-direction: column; height: 100vh; }
        .chat-box { flex-grow: 1; padding: 10px; overflow-y: auto; display: flex; flex-direction: column; }
        .input-container { display: flex; padding: 10px; }
        #user-input { flex-grow: 1; padding: 10px; border: none; border-radius: 5px; }
        button { margin-left: 10px; padding: 10px; background-color: var(--button-color); border: none; border-radius: 5px; color: #fff; cursor: pointer; }
        .message { margin: 5px 0; padding: 10px; border-radius: 5px; max-width: 70%; }
        .user-message { align-self: flex-end; background-color: var(--user-message-color); }
        .bot-message { align-self: flex-start; background-color: var(--bot-message-color); }
        .theme-selector { padding: 10px; position: absolute; top: 10px; right: 10px; background-color: #222; color: #fff; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <select id="theme-selector" class="theme-selector">
            <option value="black">Black</option>
            <option value="white">White</option>
            <option value="pink">Pink</option>
            <option value="gold">Gold</option>
            <option value="diamond">Diamond</option>
        </select>
        <div id="chat-box" class="chat-box">
            <!-- Chat messages will appear here -->
        </div>
        <div class="input-container">
            <input id="user-input" type="text" placeholder="Type a message or 'switch to query mode'..." />
            <button id="send-btn">Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendButton = document.getElementById('send-btn');
        const themeSelector = document.getElementById('theme-selector');

        let queryMode = false; // Keeps track of the mode

        // Function to append messages to the chatbox
        function appendMessage(message, isUser = true) {
            const messageDiv = document.createElement('div');
            messageDiv.textContent = message;
            messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
        }

        // Handle send button click
        sendButton.addEventListener('click', () => {
            const userMessage = userInput.value.trim();

            if (!userMessage) return;

            appendMessage(userMessage, true);

            if (userMessage.toLowerCase() === 'switch to query mode') {
                queryMode = true;
                appendMessage("Query mode activated! Type your question.", false);
            } else {
                // Fetch bot/chat or query response
                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userMessage, query_mode: queryMode })
                })
                .then(res => res.json())
                .then(data => {
                    appendMessage(data.response, false);

                    // Play the bot's voice response
                    const audio = new Audio(data.audio_path);
                    audio.play();
                });
            }

            userInput.value = ''; // Clear input field
        });

        // Theme selector event listener
        themeSelector.addEventListener('change', () => {
            const theme = themeSelector.value;
            switch (theme) {
                case 'black':
                    document.documentElement.style.setProperty('--background-color', '#000');
                    document.documentElement.style.setProperty('--text-color', '#fff');
                    document.documentElement.style.setProperty('--button-color', '#007bff');
                    document.documentElement.style.setProperty('--user-message-color', '#444');
                    document.documentElement.style.setProperty('--bot-message-color', '#555');
                    break;
                case 'white':
                    document.documentElement.style.setProperty('--background-color', '#fff');
                    document.documentElement.style.setProperty('--text-color', '#000');
                    document.documentElement.style.setProperty('--button-color', '#007bff');
                    document.documentElement.style.setProperty('--user-message-color', '#ccc');
                    document.documentElement.style.setProperty('--bot-message-color', '#ddd');
                    break;
                case 'pink':
                    document.documentElement.style.setProperty('--background-color', '#ffe4e1');
                    document.documentElement.style.setProperty('--text-color', '#000');
                    document.documentElement.style.setProperty('--button-color', '#ff69b4');
                    document.documentElement.style.setProperty('--user-message-color', '#ffc0cb');
                    document.documentElement.style.setProperty('--bot-message-color', '#ffb6c1');
                    break;
                case 'gold':
                    document.documentElement.style.setProperty('--background-color', '#ffd700');
                    document.documentElement.style.setProperty('--text-color', '#000');
                    document.documentElement.style.setProperty('--button-color', '#ffa500');
                    document.documentElement.style.setProperty('--user-message-color', '#ffe4b5');
                    document.documentElement.style.setProperty('--bot-message-color', '#ffdab9');
                    break;
                case 'diamond':
                    document.documentElement.style.setProperty('--background-color', '#e0ffff');
                    document.documentElement.style.setProperty('--text-color', '#000');
                    document.documentElement.style.setProperty('--button-color', '#00ced1');
                    document.documentElement.style.setProperty('--user-message-color', '#b0e0e6');
                    document.documentElement.style.setProperty('--bot-message-color', '#afeeee');
                    break;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True)