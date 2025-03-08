from flask import Flask, request, jsonify, send_file, render_template_string
from gtts import gTTS
import os
import random
import threading
import time
import speech_recognition as sr

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
    """Converts chatbot response to speech"""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)

    # Cleanup after 10 seconds
    threading.Thread(target=cleanup_audio, args=(filename,)).start()

    return send_file(filename, mimetype="audio/mpeg")

def cleanup_audio(*files):
    """Deletes temp audio files after 10 seconds"""
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

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
        }

        .menu-dropdown.active {
            display: block;
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

    </style>
</head>
<body>

    <!-- Dropdown Menu Button -->
    <div class="menu-container">
        <button class="menu-btn" onclick="toggleMenu()">💬</button>
        <div class="menu-dropdown">
            <button class="theme-btn" onclick="changeTheme()">Change Theme</button>
        </div>
    </div>

    <div id="chat-container"></div>

    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
        <button onclick="startVoiceInput()">🔊</button>
    </div>

    <script>
        function toggleMenu() {
            document.querySelector(".menu-dropdown").classList.toggle("active");
        }

        function changeTheme() {
            document.documentElement.style.setProperty('--primary-color', '#ff006e');
            document.documentElement.style.setProperty('--secondary-color', '#ffbe0b');
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
                
                fetch('/speak', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: data.response })
                })
                .then(res => res.blob())
                .then(blob => {
                    const audio = new Audio(URL.createObjectURL(blob));
                    audio.play();
                });
            });

            document.getElementById('user-input').value = '';
        }

        function startVoiceInput() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "en-US";

            recognition.onresult = event => {
                document.getElementById("user-input").value = event.results[0][0].transcript;
            };

            recognition.start();
        }
    </script>

</body>
</html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)