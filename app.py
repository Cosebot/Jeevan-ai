import os
import random
import threading
import time
import re
from flask import Flask, request, jsonify, send_file, render_template_string, redirect, session
from gtts import gTTS
import wikipedia
from googleapiclient.discovery import build
from supabase import create_client

# ----- Supabase Auth Init -----

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----- Flask App Init -----

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default")
app.permanent_session_lifetime = 365 * 24 * 60 * 60  # 1 year sessions

# ----- Chatbot Logic -----

english_responses = {
    "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help."],
    "how are you": ["Doing great! How about you?", "All systems go!"],
    "bye": ["Catch you later!", "Goodbye! Stay awesome!"],
}

def get_chatbot_response(user_input, name=None):
    user_input = user_input.lower().strip()
    for key, responses in english_responses.items():
        if key in user_input:
            response = random.choice(responses)
            return f"{name}, {response}" if name else response
    return f"{name}, I didn't understand that." if name else "Sorry, I didn't get that."

def detect_query_type(text):
    text = text.lower().strip()
    if text.startswith("who is") or "who is" in text:
        return "who"
    elif text.startswith("what is") or "what is" in text:
        return "what"
    elif text.startswith("where is") or "where is" in text:
        return "where"
    else:
        return "chat"

def extract_topic(text):
    match = re.search(r"(who|what|where) is (.+)", text.lower())
    if match:
        return match.group(2)
    return text.strip()

def search_wikipedia(query, sentences=2):
    try:
        summary = wikipedia.summary(query, sentences=sentences)
        return f"According to Wikipedia: {summary}"
    except wikipedia.DisambiguationError as e:
        return f"Too many results. Suggestions: {', '.join(e.options[:3])}"
    except wikipedia.PageError:
        return "Couldn't find anything."
    except Exception as e:
        return f"Error: {str(e)}"

def search_youtube_video(query):
    try:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(part="snippet", q=query, type="video", maxResults=1)
        response = request.execute()
        items = response.get("items")
        if items:
            video_id = items[0]["id"]["videoId"]
            title = items[0]["snippet"]["title"]
            return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><br>{title}'
        else:
            return "No video found."
    except Exception as e:
        return f"Error searching video: {str(e)}"

def cleanup_audio(*files):
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

# ----- Routes -----

@app.route("/")
def home():
    if "token" not in session:
        return redirect("/login")
    return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if result.session:
                session.permanent = True
                session["token"] = result.session.access_token
                session["email"] = email
                session["name"] = ""
                return redirect("/")
            return render_template_string(login_html, error="Login failed.")
        except:
            return render_template_string(login_html, error="Invalid credentials.")
    return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        result = supabase.auth.sign_up({"email": email, "password": password})
        if result.model_dump().get("error"):
            return render_template_string(signup_html, error="Signup failed.")
        return redirect("/login")
    return render_template_string(signup_html)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat", methods=["POST"])
def chat():
    if "token" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    message = request.get_json().get("message", "")
    name = session.get("name", "")
    if message.startswith("play ") or message.startswith("show me ") or message.startswith("turn on "):
        topic = message.split(" ", 1)[1]
        response = search_youtube_video(topic)
    else:
        intent = detect_query_type(message)
        if intent in ["who", "what", "where"]:
            topic = extract_topic(message)
            response = search_wikipedia(topic)
        else:
            response = get_chatbot_response(message, name)
    return jsonify({"response": response})

@app.route("/setname", methods=["POST"])
def setname():
    data = request.get_json()
    session["name"] = data.get("name", "")
    return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"])
def speak():
    text = request.get_json().get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)
    threading.Thread(target=cleanup_audio, args=(filename,)).start()
    return send_file(filename, mimetype="audio/mpeg")

# ----- HTML Templates -----

login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            background: #1b0b2e;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'SF Pro Display', sans-serif;
        }
        .login-container {
            background: rgba(255,255,255,0.1);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 0 20px #6E33B1;
            width: 300px;
        }
        input, button {
            width: 100%;
            margin: 10px 0;
            padding: 12px;
            border: none;
            border-radius: 30px;
            font-size: 16px;
        }
        button {
            background: #6E33B1;
            color: #fff;
            cursor: pointer;
        }
        button:hover {
            background: #8f45f4;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <form method="POST">
            <input name="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup")

chat_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI</title>
    <style>
        body {
            margin: 0;
            background: radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%);
            color: #EEEBF3;
            font-family: 'SF Pro Display', sans-serif;
        }
        #navbar {
            background: #6E33B1;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #navbar h2 {
            margin: 0;
        }
        #menu {
            position: relative;
        }
        #menu button {
            background: none;
            border: none;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
        }
        #dropdown {
            display: none;
            position: absolute;
            right: 0;
            background: rgba(0,0,0,0.8);
            border-radius: 10px;
            overflow: hidden;
        }
        #dropdown div {
            padding: 10px;
            cursor: pointer;
            border-bottom: 1px solid #333;
        }
        #dropdown div:hover {
            background: #444;
        }
        #chat-box {
            margin: 20px auto;
            width: 90%;
            max-width: 400px;
            height: 500px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 15px;
            overflow-y: auto;
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
            margin: 20px auto;
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
    <div id="navbar">
        <h2>Sanji AI</h2>
        <div id="menu">
            <button onclick="toggleMenu()">☰</button>
            <div id="dropdown">
                <div>Email: {{email}}</div>
                <div onclick="showSettings()">Settings</div>
                <div onclick="window.location.href='/logout'">Logout</div>
            </div>
        </div>
    </div>
    <div id="chat-box"></div>
    <div class="chat-input">
        <input type="text" id="user-input" placeholder="Type a message...">
        <button onclick="sendMessage()">Send</button>
        <button onclick="startVoiceInput()">🎤</button>
    </div>

    <div id="settings-box" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); background:#222; padding:20px; border-radius:10px; z-index:1000;">
        <h3>Settings</h3>
        <input type="text" id="name-input" placeholder="Enter your name" style="width:100%; padding:10px; margin:10px 0; border-radius:5px;">
        <button onclick="saveName()">Save</button>
        <button onclick="closeSettings()">Close</button>
    </div>

    <script>
        function toggleMenu() {
            const dropdown = document.getElementById("dropdown");
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
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
        function showSettings() {
            document.getElementById("settings-box").style.display = "block";
        }
        function closeSettings() {
            document.getElementById("settings-box").style.display = "none";
        }
        function saveName() {
            const name = document.getElementById("name-input").value;
            fetch('/setname', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name })
            });
            closeSettings();
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)