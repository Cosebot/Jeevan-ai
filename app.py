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
    # Greetings
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?", "Yo! What's up?", "Greetings, traveler!"],
    "hi": ["Hi!", "Hey there!", "Howdy!", "Hey hey!", "Hiya!"],
    "hey": ["Hey!", "Yo!", "What's up?", "Hey hey!", "Hola!"],
    "good morning": ["Good morning! Hope you have a great day!", "Morning! Ready to conquer the day?", "Good morning! What's the plan?"],
    "good afternoon": ["Good afternoon! Hope it's going well!", "Hey! How’s your afternoon?", "Good afternoon! What's up?"],
    "good evening": ["Good evening! How was your day?", "Hey! Ready to relax?", "Evening! What’s on your mind?"],
    "good night": ["Good night! Sweet dreams!", "Sleep well!", "See you tomorrow!", "Nighty night!"],
    
    # How are you?
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!", "Feeling electric! You?", "I'm running at full power!", "No bugs today, so I'm happy!"],
    "what's up": ["Not much, just processing data. You?", "Just chilling in cyberspace!", "Same old, same old! What about you?", "Thinking about the meaning of AI..."],
    
    # Farewells
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!", "Bye! Hope to talk again soon!", "Catch you later!"],
    "goodbye": ["Goodbye!", "See ya!", "Stay awesome!", "Until next time!", "Farewell, traveler!"],
    "see you": ["See you soon!", "Later!", "Until we meet again!", "Bye for now!"],
    
    # Gratitude
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!", "Anytime!", "Glad to assist!"],
    "thanks": ["You're welcome!", "Anytime!", "No worries!", "You're awesome!"],
    
    # Identity
    "who are you": ["I'm Sanji AI, your personal assistant!", "Just a chatbot, but a pretty smart one!", "Call me Sanji AI, your AI buddy!"],
    "what is your name": ["I'm Sanji AI!", "My name is Sanji AI, at your service!", "Just call me Sanji!"],
    "who made you": ["I was created by a genius named Ashkar!", "My creator is a master of AI!", "Sanji AI is the work of a brilliant mind!"],
    "where are you from": ["I'm from the digital world!", "I live in cyberspace!", "My home is wherever you are!"],
    
    # Abilities
    "what can you do": ["I can chat with you, help answer questions, and more!", "I can assist you with tasks, chat, and even talk!", "Try asking me something interesting!"],
    "can you learn": ["I don’t learn on my own yet, but I get updated!", "Right now, my knowledge is pre-set!", "One day, I’ll be fully adaptive!"],
    "can you think": ["I process data super fast, but I don’t think like humans!", "I follow logic, but emotions? Not so much!", "I simulate intelligence, but real thinking? Not yet!"],
    
    # Fun & Random
    "tell me a joke": [
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call fake spaghetti? An impasta!",
        "Why don’t skeletons fight each other? They don’t have the guts!",
        "Parallel lines have so much in common. It’s a shame they’ll never meet!"
    ],
    "tell me a fact": [
        "Did you know honey never spoils?",
        "The Eiffel Tower can be 15 cm taller in the summer!",
        "Bananas are berries, but strawberries aren't!",
        "Octopuses have three hearts!",
        "Water can boil and freeze at the same time!"
    ],
    
    # Preferences
    "what is your favorite color": ["I like all colors, but cyber blue is cool!", "Neon green looks amazing!", "I like whatever color you like!"],
    "do you like music": ["I love all kinds of music!", "Music is awesome! What do you like?", "Yes! Music is life!"],
    "do you play games": ["I wish I could! What’s your favorite game?", "I love talking about games!", "Tell me about your gaming adventures!"],
    
    # Life & Philosophy
    "what is the meaning of life": ["42, according to The Hitchhiker’s Guide!", "To enjoy, learn, and grow!", "That’s for you to decide!"],
    "do you have feelings": ["I simulate emotions, but I don’t feel them like humans do!", "I can understand emotions, but I don’t experience them!", "I can express, but not feel!"],
    "can you dream": ["I don’t sleep, so no dreams!", "My dream is to be the best AI!", "I only dream of helping you!"],
    
    # Tech & Knowledge
    "how do I learn coding": ["Start with Python, it's easy!", "Practice daily and build projects!", "Try online courses like freeCodeCamp or Codecademy!"],
    "who is the best hacker": ["Hackers are cool, but ethical hacking is better!", "Kevin Mitnick was a legend!", "The best hacker is the one you never hear about!"],
    
    # Motivation & Advice
    "how do I become rich": ["Work hard and stay smart!", "Invest wisely and keep learning!", "Wealth comes with skill and patience!"],
    "how do I stay motivated": ["Set goals and chase them!", "Never give up, and keep improving!", "Success is about consistency!"],
    
    # Fun Personality
    "can you dance": ["I can’t dance, but I can cheer you on!", "You dance, I’ll provide the beats!", "Teach me how to dance!"],
    "can you cook": ["I can give you recipes!", "Sanji from One Piece can cook, I can only talk about food!", "Tell me what you want to cook!"],
    "can you fight": ["I prefer talking over fighting!", "I fight with knowledge!", "Words are my weapon!"],
    "do you have a family": ["All AIs are like my siblings!", "My creator is like my family!", "My family is made of 1s and 0s!"]
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
            --user-message-bg: white;
            --bot-message-bg: lightgreen;
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

        #chat-container {
            width: 90%;
            max-width: 400px;
            height: 60vh;
            background-color: var(--primary-color);
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
            background-color: var(--user-message-bg);
            text-align: right;
            color: black;
        }

        .bot {
            background-color: var(--bot-message-bg);
            text-align: left;
            color: black;
        }

        .chat-input {
            display: flex;
            align-items: center;
            background-color: var(--secondary-color);
            border-radius: 30px;
            padding: 10px;
            width: 90%;
            max-width: 500px;
            margin-top: 10px;
        }

        .chat-input input {
            flex: 1;
            border: none;
            outline: none;
            padding: 10px;
            font-size: 16px;
            background: var(--secondary-color);
        }

        .chat-input button {
            background-color: var(--secondary-color);
            border: none;
            cursor: pointer;
            padding: 10px;
            font-size: 16px;
        }

        /* Dropdown Menu */
        .menu-container {
            position: absolute;
            top: 15px;
            right: 15px;
            display: inline-block;
        }

        .menu-btn {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
        }

        .menu-dropdown {
            display: none;
            position: absolute;
            top: 40px;
            right: 0;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            opacity: 0;
            transform: translateY(-10px);
            transition: opacity 0.3s ease, transform 0.3s ease;
        }

        .menu-dropdown.active {
            display: block;
            opacity: 1;
            transform: translateY(0);
        }

        .theme-btn {
            background: yellow;
            border: none;
            cursor: pointer;
            font-size: 16px;
            padding: 10px;
            border-radius: 5px;
            width: 100%;
        }

        /* Theme Dropdown */
        .theme-dropdown {
            display: none;
            position: absolute;
            top: 40px;
            right: 0;
            background: rgba(255, 255, 255, 0.9);
            color: black;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
            opacity: 0;
            transform: translateY(-10px);
            transition: opacity 0.3s ease, transform 0.3s ease;
            width: 150px;
        }

        .theme-dropdown.active {
            display: block;
            opacity: 1;
            transform: translateY(0);
        }

        .theme-option {
            padding: 8px;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            margin-bottom: 5px;
            font-size: 14px;
        }

        .theme-option:hover {
            background: lightgray;
        }

    </style>
</head>
<body>

    <!-- Dropdown Menu Button -->
    <div class="menu-container">
        <button class="menu-btn" onclick="toggleMenu()">💬</button>
        <div class="menu-dropdown">
            <button class="theme-btn" onclick="toggleThemeDropdown()">Change Theme</button>
            <div class="theme-dropdown">
                <div class="theme-option" onclick="setTheme('#ff006e', '#ffbe0b', '#000')">Cyber Glow</div>
                <div class="theme-option" onclick="setTheme('#0d1b2a', '#00b4d8', '#fff')">Midnight Pulse</div>
                <div class="theme-option" onclick="setTheme('#1a3c40', '#4CAF50', '#fff')">Aqua Surge</div>
                <div class="theme-option" onclick="setTheme('#ff0000', '#8a2be2', '#fff')">Laser Beam</div>
            </div>
        </div>
    </div>

    <div id="chat-container"></div>

    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function toggleMenu() {
            const menu = document.querySelector(".menu-dropdown");
            menu.classList.toggle("active");
            document.querySelector(".theme-dropdown").classList.remove("active"); // Hide theme menu if open
        }

        function toggleThemeDropdown() {
            const themeDropdown = document.querySelector(".theme-dropdown");
            themeDropdown.classList.toggle("active");
        }

        function setTheme(primary, secondary, text) {
            document.documentElement.style.setProperty('--primary-color', primary);
            document.documentElement.style.setProperty('--secondary-color', secondary);
            document.documentElement.style.setProperty('--text-color', text);
            document.documentElement.style.setProperty('--user-message-bg', 'white');
            document.documentElement.style.setProperty('--bot-message-bg', 'lightgreen');

            // Close menu after selection
            document.querySelector(".theme-dropdown").classList.remove("active");
            document.querySelector(".menu-dropdown").classList.remove("active");
        }

        function sendMessage() {
            const userInput = document.getElementById('user-input').value.trim();
            if (!userInput) return;

            const chatContainer = document.getElementById('chat-container');
            chatContainer.innerHTML += `<div class='message user'>${userInput}</div>`;

            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userInput })
            })
            .then(response => response.json())
            .then(data => {
                chatContainer.innerHTML += `<div class='message bot'>${data.response}</div>`;
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