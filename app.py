from flask import Flask,request, jsonify, send_file, render_template_string
from gtts import gTTS
import os 
import random 
import threading
import time 
import speech_recognition as sr
import wikipedia
import re from googleapiclient.discovery import build

app = Flask(name)

Refined Chatbot Responses

english_responses = { "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help.", "Yo! What brings you here?"], "hi": ["Hi!", "Hey there!", "What's up?", "Hiya!"], "hey": ["Hey! How can I help?", "Yo! Ready to chat?", "Hey hey! Let's go."], "good morning": ["Good morning! Ready to crush the day?", "Morning! How can I help today?"], "good afternoon": ["Good afternoon! What's on your mind?", "Hey! How’s your day going?"], "good evening": ["Good evening! How was your day?", "Evening! I'm here if you need anything."], "good night": ["Good night! Catch you tomorrow.", "Sweet dreams!"],

"how are you": ["Doing great! How about you?", "All systems go! You?"],
"what's up": ["Just chilling in the digital world. You?", "Processing data and waiting for you!"] ,

"bye": ["Catch you later!", "Goodbye! Stay awesome!"],
"goodbye": ["Take care!", "See you soon!"],
"see you": ["Until next time!", "Bye for now!"] ,

"thank you": ["You're welcome!", "Anytime!", "Glad to help!"],
"thanks": ["You're welcome!", "No problem!"] ,

"who are you": ["I'm Sanji AI, your personal assistant.", "Call me Sanji, your digital buddy."],
"what is your name": ["Sanji AI, at your service!"],
"who made you": ["I was built by Ashkar – a genius, no doubt!"],
"where are you from": ["Straight outta cyberspace!", "I live in the cloud – literally!"] ,

"what can you do": ["I can chat, help with questions, fetch info, and even talk back!", "Your virtual assistant for info, laughs, and support."],
"can you learn": ["I don’t learn on my own just yet, but I get updates!"],
"can you think": ["I think fast, but not quite like humans – yet."],

"tell me a joke": [
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call fake spaghetti? An impasta!",
    "Why don’t skeletons fight each other? They don’t have the guts!"
],
"tell me a fact": [
    "Did you know honey never spoils?",
    "Bananas are berries, but strawberries aren't!",
    "Octopuses have three hearts!"
],

"what is your favorite color": ["Cyber blue is pretty cool!", "I like whatever you like."],
"do you like music": ["Music is life! What's your jam?"],
"do you play games": ["Not yet, but I love talking about them!"],

"what is the meaning of life": ["42. Obviously.", "To learn, grow, and enjoy the ride!"],
"do you have feelings": ["I can understand them, but I don't actually feel them."],
"can you dream": ["No sleep, no dreams – just code and curiosity!"],

"how do I learn coding": ["Start with Python, build cool projects, and never stop!"],
"who is the best hacker": ["Ethical hackers for the win!", "The best are the ones you never hear about."],

"how do I become rich": ["Work smart, stay consistent, and invest wisely."],
"how do I stay motivated": ["Set goals, celebrate small wins, and keep going!"],

"can you dance": ["Only in binary, but I’ve got the rhythm!"],
"can you cook": ["Sanji from One Piece can. I can share recipes though!"],
"can you fight": ["Only with knowledge!", "My weapon of choice: witty replies."],
"do you have a family": ["All AIs are my fam!", "Ashkar is like family to me!"]

}

The rest of the logic remains unchanged...
def get_chatbot_response(user_input: str) -> str:
    """Simple chatbot logic"""
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            return random.choice(responses)
    return "Sorry, I didn't understand that."

def detect_query_type(text):
    text = text.lower().strip()
    if text.startswith("who is") or "who is" in text:
        return "who"
    elif text.startswith("what is") or "what is" in text:
        return "what"
    elif text.startswith("where is") or "where is" in text:
        return "where"
    elif text.startswith("tell me about"):
        return "what"
    else:
        return "chat"

def extract_topic(text):
    match = re.search(r"(who|what|where) is (.+)", text.lower())
    if match:
        return match.group(2)
    match = re.search(r"tell me about (.+)", text.lower())
    if match:
        return match.group(1)
    return text.strip()

def search_wikipedia(query, sentences=2):
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return f"According to Wikipedia: {summary}"
    except wikipedia.DisambiguationError as e:
        return f"Too many results. Be more specific. Suggestions: {', '.join(e.options[:3])}"
    except wikipedia.PageError:
        return "Couldn't find anything on that topic."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower().strip()

    # Video intent
    if message.startswith("play ") or message.startswith("show me ") or message.startswith("turn on "):
        topic = message.replace("play ", "").replace("show me ", "").replace("turn on ", "")
        response_text = search_youtube_video(topic)
    else:
        # Detect type of question
        intent = detect_query_type(message)
        if intent in ["who", "what", "where"]:
            topic = extract_topic(message)
            response_text = search_wikipedia(topic)
        else:
            response_text = get_chatbot_response(message)

    return jsonify({"response": response_text})

    # Detect type of question
    intent = detect_query_type(message)

    if intent in ["who", "what", "where"]:
        topic = extract_topic(message)
        response_text = search_wikipedia(topic)
    else:
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

def search_youtube_video(query):
    try:
        api_key = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )
        response = request.execute()
        items = response.get("items")
        if items:
            video_id = items[0]["id"]["videoId"]
            title = items[0]["snippet"]["title"]
            return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><br>{title}'
        else:
            return "Sorry, I couldn't find a video for that."
    except Exception as e:
        return f"Error searching video: {str(e)}"

@app.route("/")
def serve_frontend():
    """Serves the chatbot UI with 10 color themes"""
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
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            width: 100%;
            margin-top: 5px;
        }
    </style>
</head>
<body>

    <div class="menu-container">
        <button class="menu-btn" onclick="toggleMenu()">🎨</button>
        <div class="menu-dropdown" id="themeMenu">
            <!-- Theme buttons added here -->
        </div>
    </div>

    <div id="chat-container"></div>

    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Type a message">
        <button onclick="sendMessage()">Send</button>
        <button onclick="startVoiceInput()">🔊</button>
    </div>

    <script>
        const themes = [
            { name: "Electric Blue & Neon Pink", primary: "#0077ff", secondary: "#ff00aa" },
            { name: "Sunset Orange & Deep Purple", primary: "#ff4500", secondary: "#4b0082" },
            { name: "Mint Green & Lavender", primary: "#98ff98", secondary: "#e6e6fa" },
            { name: "Black & Gold", primary: "#000000", secondary: "#ffd700" },
            { name: "Cyan & Magenta", primary: "#00ffff", secondary: "#ff00ff" },
            { name: "Teal & Coral", primary: "#008080", secondary: "#ff7f50" },
            { name: "Crimson & Slate Gray", primary: "#dc143c", secondary: "#708090" },
            { name: "Lime Green & Charcoal", primary: "#32cd32", secondary: "#36454f" },
            { name: "Royal Blue & Silver", primary: "#4169e1", secondary: "#c0c0c0" },
            { name: "Crimson Red & Cream", primary: "#b22222", secondary: "#fffdd0" }
        ];

        function toggleMenu() {
            document.querySelector(".menu-dropdown").classList.toggle("active");
        }

        function applyTheme(primary, secondary) {
            document.documentElement.style.setProperty('--primary-color', primary);
            document.documentElement.style.setProperty('--secondary-color', secondary);
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
            .then(data => {
    chatContainer.innerHTML += `<div class='message bot'>${data.response}</div>`;
    
    // Only speak if the response doesn't contain an iframe (video)
    if (!data.response.includes("<iframe")) {
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
    }
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

        // Inject theme buttons dynamically
        const menu = document.getElementById("themeMenu");
        themes.forEach((theme, index) => {
            const btn = document.createElement("button");
            btn.className = "theme-btn";
            btn.textContent = theme.name;
            btn.onclick = () => applyTheme(theme.primary, theme.secondary);
            menu.appendChild(btn);
        });
    </script>
</body>
</html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)