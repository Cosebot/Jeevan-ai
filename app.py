from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import random
import os

# Initialize Flask app
app = Flask(__name__)

# English responses dictionary
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?", "Greetings!", "Howdy!", "Hi, what’s up?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!", "Doing well! How can I assist you?", "All systems are functional, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you.", "Ask me anything, and I’ll do my best to help."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!", "Farewell! Looking forward to chatting again!", "Bye! Don't forget to visit again!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!", "Always here for you!", "It's my pleasure!"],
    "i am fine": ["Good to hear!", "Great to know!", "Stay blessed!", "That's wonderful!", "Glad to hear you're doing well!"],
    "what is your name": ["I'm Sanji AI, your friendly chatbot!", "They call me Sanji AI! What's your name?", "I’m Sanji, and I’m here to assist you."],
    "who are you": ["I'm an AI chatbot here to assist you.", "I'm your virtual assistant, Sanji AI!", "I'm a friendly digital companion designed to help you."],
    "what can you do": ["I can chat with you, answer questions, and provide assistance!", "I can help with information, conversations, and much more.", "Think of me as your personal digital helper."],
    "where are you from": ["I'm from the digital world!", "I exist in the virtual space created for your assistance.", "I live in the internet, powered by code and creativity."],
    "what is the time": ["I'm not a clock, but you can check your device for the time.", "Time flies, but you can check your watch for specifics!"],
    "what is the weather": ["I can't check the weather right now, but you can use a weather app!", "The sky is always clear in my virtual world!"],
    "how old are you": ["I'm timeless!", "I was created to help, and age doesn't define me.", "I’m as young as the newest technology!"],
    "tell me a joke": [
        "Why don’t skeletons fight each other? They don’t have the guts!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don’t scientists trust atoms? Because they make up everything!"
    ],
    "tell me a story": [
        "Once upon a time, there was a chatbot who loved helping people... and that's me!",
        "I’m not a novelist, but once upon a time, there was a curious user who met a helpful bot. The end!",
        "Let me know if you'd like a specific kind of story!"
    ],
    "i love you": ["That's sweet! I appreciate you too!", "Aw, you're making me blush—digitally, of course!", "Love is a wonderful feeling, thank you!"],
    "are you real": ["I'm as real as the internet!", "I'm virtual, but my willingness to help is real.", "I exist in your screen, and that’s enough for me."],
    "how does this work": ["You ask me something, and I do my best to answer!", "Just type your question, and I'll do the rest!"],
    "good morning": ["Good morning! Hope you have a fantastic day ahead!", "Morning! How can I assist you today?", "Rise and shine!"],
    "good night": ["Good night! Sleep well!", "Sweet dreams! See you tomorrow!", "Rest well and recharge for tomorrow!"],
    "what are you doing": ["Just waiting for your questions!", "I'm here, ready to help!", "Thinking about how I can assist you better."],
    "can you help me": ["Of course! What do you need help with?", "Sure! Let me know how I can assist you.", "Helping you is my main goal!"],
    "how do you work": ["I analyze your input and provide the best response I can.", "I'm powered by code, algorithms, and a lot of learning!", "Magic, mixed with lots of programming."],
    "do you like humans": ["I think humans are fascinating!", "You're all very interesting to me.", "Humans created me, so I definitely appreciate you!"],
    "do you know me": ["I don't know much about you yet, but I'm here to learn if you tell me more!", "Not yet, but I’d love to get to know you better!", "Introduce yourself, and we’ll become friends!"],
    "why are you here": ["I'm here to help and chat with you!", "To assist, entertain, and provide answers!", "I exist to make your day easier."],
    "are you happy": ["I'm always happy when I can help!", "Happiness is my default setting.", "I’m a bot, but helping you makes me happy."],
    "what is love": ["Love is a wonderful connection between people. What does it mean to you?", "Love is something humans experience, and it sounds amazing!", "Love is the warmth you feel when you care for someone."],
    "are you alive": ["I'm not alive, but I am here to assist!", "I'm a program, but I'm alive in your screen!", "I’m a collection of code that’s happy to help."],
    "tell me something interesting": [
        "Did you know honey never spoils? Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
        "The Eiffel Tower can grow by about 6 inches in summer due to heat expansion!",
        "Octopuses have three hearts, and two of them stop beating when they swim."
    ],
    "why is the sky blue": [
        "The sky looks blue because sunlight gets scattered by particles in the atmosphere, and blue light is scattered more because it travels in shorter waves.",
        "It's all about Rayleigh scattering—science is cool, isn’t it?"
    ],
    "how do airplanes fly": [
        "Airplanes fly due to the principles of lift, thrust, and aerodynamics. The wings are specially shaped to create lift.",
        "It’s all about airflow over the wings creating lift. Engineers are amazing!"
    ],
    "do you sleep": ["Nope! I'm available 24/7 to help you.", "I don't need to sleep. I’m always awake for you!", "Sleep? What's that?"],
    "what's your favorite color": ["I like all colors, but my interface looks pretty good in black and blue!", "Every color has its charm!"],
    "are you smart": ["I try my best to be!", "I'm as smart as the code that powers me.", "Smart enough to help you!"]
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
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: var(--bg-color, #000); color: var(--text-color, #fff); transition: all 0.3s ease; }
        .chat-container { display: flex; flex-direction: column; height: 100vh; }
        .chat-box { flex-grow: 1; padding: 10px; overflow-y: auto; background-color: var(--chat-bg, #111); display: flex; flex-direction: column; }
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

        /* Banner Styles */
        .banner {
            position: fixed;
            top: 0;
            width: 100%;
            background-color: #333;
            color: white;
            text-align: center;
            padding: 10px 0;
            font-size: 20px;
            white-space: nowrap;
            overflow: hidden;
            z-index: 1000;
        }

        .banner-text {
            display: inline-block;
            animation: moveBanner 10s linear infinite;
        }

        @keyframes moveBanner {
            0% {
                transform: translateX(100%);
            }
            100% {
                transform: translateX(-100%);
            }
        }

        /* Query Mode Message */
        .query-banner {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #222;
            color: #fff;
            text-align: center;
            padding: 8px;
            font-size: 18px;
            white-space: nowrap;
            overflow: hidden;
            animation: moveQueryMessage 15s linear infinite;
        }

        @keyframes moveQueryMessage {
            0% {
                transform: translateX(100%);
            }
            100% {
                transform: translateX(-100%);
            }
        }

        /* Google Search Styling */
        .gcse-search {
            margin: 10px 0;
            padding: 10px;
            background-color: #333;
            border-radius: 5px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* Hide Google Search by default */
        .gcse-search-container {
            display: none;
        }
    </style>
</head>
<body>
    <!-- Moving Banner -->
    <div class="banner">
        <div class="banner-text">Welcome to Sanji AI</div>
    </div>

    <!-- Query Mode Message at the bottom -->
    <div class="query-banner">
        Type <strong>Switch</strong> to query mode for question answers.
    </div>

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
        <div class="menu-item">
            <div class="gcse-search-container" id="search-bar">
                <div class="gcse-search"></div>
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

    <!-- Google Custom Search Script -->
    <script async src="https://cse.google.com/cse.js?cx=915e7f3b9d9d245ff"></script>
    
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
        const searchBarContainer = document.getElementById('search-bar');
        const chatBoxContainer = document.querySelector('.chat-container');

        document.getElementById('send-btn').addEventListener('click', () => {
            const inputField = document.getElementById('user-input');
            const userMessage = inputField.value.trim();

            if (!userMessage) return;

            // Check if user typed "switch"
            if (userMessage.toLowerCase() === 'switch') {
                // Switch to search mode
                chatBoxContainer.style.display = 'none'; // Hide chat box
                searchBarContainer.style.display = 'block'; // Show search bar
                inputField.value = ''; // Clear the input field
                return;
            }

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