from flask import Flask, request, jsonify, send_file, render_template_string
from gtts import gTTS
import os 
import random 
import threading
import time 
import speech_recognition as sr
import wikipedia
import re
from googleapiclient.discovery import build

app = Flask(__name__)

english_responses = {
    "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help.", "Yo! What brings you here?"],
    "hi": ["Hi!", "Hey there!", "What's up?", "Hiya!"],
    "hey": ["Hey! How can I help?", "Yo! Ready to chat?", "Hey hey! Let's go."],
    "good morning": ["Good morning! Ready to crush the day?", "Morning! How can I help today?"],
    "good afternoon": ["Good afternoon! What's on your mind?", "Hey! How’s your day going?"],
    "good evening": ["Good evening! How was your day?", "Evening! I'm here if you need anything."],
    "good night": ["Good night! Catch you tomorrow.", "Sweet dreams!"],
    "how are you": ["Doing great! How about you?", "All systems go! You?"],
    "what's up": ["Just chilling in the digital world. You?", "Processing data and waiting for you!"],
    "bye": ["Catch you later!", "Goodbye! Stay awesome!"],
    "goodbye": ["Take care!", "See you soon!"],
    "see you": ["Until next time!", "Bye for now!"],
    "thank you": ["You're welcome!", "Anytime!", "Glad to help!"],
    "thanks": ["You're welcome!", "No problem!"],
    "who are you": ["I'm Sanji AI, your personal assistant.", "Call me Sanji, your digital buddy."],
    "what is your name": ["Sanji AI, at your service!"],
    "who made you": ["I was built by Ashkar – a genius, no doubt!"],
    "where are you from": ["Straight outta cyberspace!", "I live in the cloud – literally!"],
    "what can you do": ["I can chat, help with questions, fetch info, and even talk back!", "Your virtual assistant for info, laughs, and support."],
    "can you learn": ["I don’t learn on my own just yet, but I get updates!"],
    "can you think": ["I think fast, but not quite like humans – yet."],
    "tell me a joke": ["Why did the scarecrow win an award? Because he was outstanding in his field!", "What do you call fake spaghetti? An impasta!", "Why don’t skeletons fight each other? They don’t have the guts!"],
    "tell me a fact": ["Did you know honey never spoils?", "Bananas are berries, but strawberries aren't!", "Octopuses have three hearts!"],
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

def get_chatbot_response(user_input: str) -> str:
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

@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)
    threading.Thread(target=cleanup_audio, args=(filename,)).start()
    return send_file(filename, mimetype="audio/mpeg")

def cleanup_audio(*files):
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

def search_youtube_video(query):
    try:
        api_key = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(part="snippet", q=query, type="video", maxResults=1)
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

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower().strip()

    # If the message starts with play/show me/turn on, search YouTube
    if message.startswith("play ") or message.startswith("show me ") or message.startswith("turn on "):
        topic = message.split(" ", 1)[1]
        response_text = search_youtube_video(topic)
    else:
        intent = detect_query_type(message)
        if intent in ["who", "what", "where"]:
            topic = extract_topic(message)
            response_text = search_wikipedia(topic)
        else:
            response_text = get_chatbot_response(message)

    return jsonify({"response": response_text})

@app.route("/")
def serve_frontend():
    html_content = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>Sanji AI</title>
        <style>
            body {
                margin: 0;
                font-family: 'SF Pro Display', sans-serif;
                background: radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%);
                color: #EEEBF3;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                overflow: hidden;
            }
            .btn {
                width: 200px;
                padding: 12px;
                margin: 10px;
                border-radius: 30px;
                font-size: 16px;
                cursor: pointer;
                border: none;
                background: #6E33B1;
                color: #fff;
                box-shadow: 0 0 10px #6E33B1;
            }
            .btn:hover {
                background: #8f45f4;
            }
            #chat-container {
                display: none;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                width: 100%;
                height: 100vh;
            }
            #chat-box {
                width: 90%;
                max-width: 400px;
                height: 60vh;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                padding: 15px;
                margin-top: 20px;
                overflow-y: auto;
                backdrop-filter: blur(10px);
                box-shadow: 0 0 20px #6E33B1;
            }
            .message {
                padding: 10px 15px;
                margin: 10px 0;
                border-radius: 12px;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user {
                background: #38E6A2;
                align-self: flex-end;
                text-align: right;
                color: #0E0307;
            }
            .bot {
                background: #6E33B1;
                align-self: flex-start;
                text-align: left;
                color: #EEEBF3;
            }
            .chat-input {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 20px 0;
                width: 90%;
                max-width: 400px;
            }
            .chat-input input {
                flex: 1;
                padding: 12px;
                border-radius: 30px;
                border: none;
                outline: none;
                background: #C0B4E3;
                color: #0E0307;
                font-size: 16px;
            }
            .chat-input button {
                background: #6E33B1;
                color: #fff;
                border: none;
                border-radius: 30px;
                padding: 10px 15px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="auth-screen">
            <h1 class="glow">Elevate your thinking</h1>
            <p>Discover endless ways our AI can enhance your happiness,thinking and a companionship</p>
            <button class="btn" onclick="enterChat()">Enter Sanji AI</button>
        </div>
        <div id="chat-container">
            <div id="chat-box"></div>
            <div class="chat-input">
                <input type="text" id="user-input" placeholder="Type a message...">
                <button onclick="sendMessage()">Send</button>
                <button onclick="startVoiceInput()">🎤</button>
            </div>
        </div>
        <script>
            function enterChat() {
                document.getElementById("auth-screen").style.display = "none";
                document.getElementById("chat-container").style.display = "flex";

                const message = "Welcome to Sanji AI";
                const chat = document.getElementById("chat-box");
                const bubble = document.createElement("div");
                bubble.className = "message bot";
                bubble.innerHTML = "";
                chat.appendChild(bubble);

                let i = 0;
                const typing = setInterval(() => {
                    if (i < message.length) {
                        bubble.innerHTML += message.charAt(i);
                        i++;
                    } else {
                        clearInterval(typing);
                        fetch('/speak', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: message })
                        })
                        .then(res => res.blob())
                        .then(blob => {
                            const audio = new Audio(URL.createObjectURL(blob));
                            audio.play();
                        });
                    }
                }, 50);
            }

            function sendMessage() {
                const input = document.getElementById("user-input");
                const message = input.value.trim();
                if (!message) return;
                const chat = document.getElementById("chat-box");
                chat.innerHTML += `<div class='message user'>${message}</div>`;
                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                })
                .then(res => res.json())
                .then(data => {
                    chat.innerHTML += `<div class='message bot'>${data.response}</div>`;
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
                input.value = "";
            }

            function startVoiceInput() {
                const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                recognition.lang = "en-US";
                recognition.onresult = e => {
                    document.getElementById("user-input").value = e.results[0][0].transcript;
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