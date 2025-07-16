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
app.permanent_session_lifetime = 365 * 24 * 60 * 60  # 1 year

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
    text = text.lower()
    for keyword in ["play", "show me", "turn on", "video of"]:
        if keyword in text:
            return text.split(keyword, 1)[1].strip()
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

def get_theme_gradient(theme):
    gradients = {
        "default": "radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%)",
        "cyan-purple": "linear-gradient(135deg, #00bcd4, #8e24aa)",
        "green-yellow": "linear-gradient(135deg, #8bc34a, #ffeb3b)",
        "pink-orange": "linear-gradient(135deg, #ff4081, #ff9100)"
    }
    return gradients.get(theme, gradients["default"])

# ----- Routes -----
@app.route("/")
def index():
    return redirect("/login")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            print(f"[LOGIN] Attempting login for: {email}")
            result = supabase.auth.sign_in_with_password({"email": email, "password": password})

            if result and hasattr(result, "session") and result.session:
                session.permanent = True
                session["token"] = result.session.access_token
                session["email"] = email
                session["name"] = ""
                session["theme"] = "default"
                print("[LOGIN] Success — Redirecting to /chat")
                return redirect("/chat")
            else:
                print("[LOGIN] Failed — Invalid credentials or no session")
                return render_template_string("<h1>Login Failed</h1><p>Invalid email or password.</p>")
        
        except Exception as e:
            print("[LOGIN ERROR]:", e)
            return render_template_string(f"<h1>Login Failed</h1><p>{str(e)}</p>")
    
    return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        result = supabase.auth.sign_up({"email": email, "password": password})
        if result.model_dump().get("error"):
            return render_template_string(signup_html)
        return redirect("/login")
    return render_template_string(signup_html)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat")
def chat_page():
    if "token" not in session:
        return redirect("/login")
    theme = get_theme_gradient(session.get("theme", "default"))
    return render_template_string(chat_html, email=session.get("email", ""), theme_gradient=theme)

@app.route("/chat", methods=["POST"])
def chat():
    if "token" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    message = request.get_json().get("message", "")
    name = session.get("name", "")
    if any(keyword in message.lower() for keyword in ["play", "show me", "turn on", "video of"]):
        topic = extract_topic(message)
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

@app.route("/settheme", methods=["POST"])
def settheme():
    data = request.get_json()
    session["theme"] = data.get("theme", "default")
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

@app.route("/settings")
def settings():
    if "token" not in session:
        return redirect("/login")
    theme = get_theme_gradient(session.get("theme", "default"))
    return render_template_string(settings_html, email=session.get("email", ""), theme_gradient=theme)
# ----- HTML Templates -----
login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {background: #1b0b2e; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'SF Pro Display', sans-serif; margin: 0;}
        .container {background: rgba(255,255,255,0.1); padding: 40px 30px; border-radius: 20px; box-shadow: 0 0 20px #6E33B1; width: 90%; max-width: 400px;}
        .container input, .container button {width: 100%; margin: 12px 0; padding: 14px; border: none; border-radius: 30px; font-size: 16px; box-sizing: border-box;}
        .container button {background: #6E33B1; color: #fff; cursor: pointer; transition: background 0.3s ease;}
        .container button:hover {background: #8f45f4;}
        .link-button {background: none; color: #8f45f4; border: none; text-decoration: underline; cursor: pointer; display: block; margin: 10px auto 0; font-size: 16px;}
    </style>
</head>
<body>
    <div class="container">
        <form method="POST">
            <input name="email" type="email" placeholder="Email" required>
            <input name="password" type="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        <button class="link-button" onclick="window.location.href='/signup'">New user? Sign Up</button>
    </div>
</body>
</html>
"""

signup_html = login_html.replace("Login", "Sign Up").replace("/signup", "/login").replace("New user?", "Already a user?")

chat_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {margin: 0; background: {{theme_gradient}}; color: #EEEBF3; font-family: 'SF Pro Display', sans-serif; height: 100vh; overflow: hidden; display: flex; flex-direction: column;}
        #navbar {background: #6E33B1; padding: 10px; display: flex; justify-content: space-between; align-items: center;}
        #navbar h2 {margin: 0;}
        #menu button {background: none; border: none; color: #fff; font-size: 28px; cursor: pointer;}
        #dropdown {display: none; position: absolute; right: 10px; top: 50px; background: rgba(0,0,0,0.8); border-radius: 10px; overflow: hidden; z-index: 1000;}
        #dropdown div {padding: 12px 16px; cursor: pointer; border-bottom: 1px solid #333;}
        #dropdown div:hover {background: #444;}
        #chat-box {flex: 1; width: 100%; max-width: 400px; margin: auto; background: rgba(255,255,255,0.05); border-radius: 20px; padding: 15px; overflow-y: auto;}
        .message {padding: 10px 15px; margin: 10px 0; border-radius: 12px; max-width: 80%; word-wrap: break-word;}
        .user {background: #38E6A2; align-self: flex-end; text-align: right; color: #0E0307;}
        .bot {background: #6E33B1; align-self: flex-start; text-align: left; color: #EEEBF3;}
        .chat-input {display: flex; align-items: center; gap: 10px; margin: 10px auto; width: 90%; max-width: 400px;}
        .chat-input input {flex: 1; padding: 12px; border-radius: 30px; border: none; outline: none; background: #C0B4E3; color: #0E0307; font-size: 16px;}
        .chat-input button {background: #6E33B1; color: #fff; border: none; border-radius: 30px; padding: 10px 15px; cursor: pointer;}
    </style>
</head>
<body>
    <div id="navbar">
        <h2>Sanji AI</h2>
        <div id="menu">
            <button onclick="toggleMenu()">☰</button>
            <div id="dropdown">
                <div>Email: {{email}}</div>
                <div onclick="window.location.href='/settings'">Settings</div>
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
            fetch('/chat', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message })})
            .then(res => res.json())
            .then(data => {
                chat.innerHTML += `<div class='message bot'>${data.response}</div>`;
                fetch('/speak', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ text: data.response })})
                .then(res => res.blob())
                .then(blob => {new Audio(URL.createObjectURL(blob)).play();});
            });
            input.value = "";
        }
        function startVoiceInput() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = "en-US";
            recognition.onresult = e => {document.getElementById("user-input").value = e.results[0][0].transcript;};
            recognition.start();
        }
    </script>
</body>
</html>
"""

settings_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Settings</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {background: {{theme_gradient}}; color: #fff; font-family: 'SF Pro Display', sans-serif; margin: 0; padding: 20px;}
        h2 {text-align: center; margin-bottom: 20px;}
        label {display: block; margin-top: 20px; font-size: 18px;}
        input, textarea {width: 100%; padding: 12px; margin-top: 5px; border-radius: 10px; border: none; font-size: 16px; box-sizing: border-box;}
        .theme-button {margin: 10px 0; width: 100%; padding: 15px; border: none; border-radius: 20px; font-size: 16px; cursor: pointer; color: #fff;}
        button {margin-top: 20px; padding: 12px; width: 100%; border-radius: 30px; background: #6E33B1; color: #fff; border: none; cursor: pointer;}
        button:hover {background: #8f45f4;}
    </style>
</head>
<body>
    <button onclick="window.location.href='/chat'" style="background:none;border:none;color:#8f45f4;font-size:20px;cursor:pointer;">← Back</button>
    <h2>Settings</h2>
    <label for="name">Name:</label>
    <input type="text" id="name" placeholder="Enter your name">
    <button onclick="saveName()">Save Name</button>

    <label>Themes:</label>
    <button class="theme-button" style="background: radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%);" onclick="setTheme('default')">Default (Purple)</button>
    <button class="theme-button" style="background: linear-gradient(135deg, #00bcd4, #8e24aa);" onclick="setTheme('cyan-purple')">Cyan & Purple</button>
    <button class="theme-button" style="background: linear-gradient(135deg, #8bc34a, #ffeb3b);" onclick="setTheme('green-yellow')">Green & Yellow</button>
    <button class="theme-button" style="background: linear-gradient(135deg, #ff4081, #ff9100);" onclick="setTheme('pink-orange')">Pink & Orange</button>

    <label for="feedback">Feedback:</label>
    <textarea id="feedback" rows="4" placeholder="Share your thoughts..."></textarea>
    <button onclick="submitFeedback()">Submit Feedback</button>
    <button onclick="window.location.href='/logout'">Logout</button>

    <script>
        function saveName() {
            const name = document.getElementById("name").value;
            fetch('/setname', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ name })});
            alert("Name saved!");
        }
        function setTheme(theme) {
            fetch('/settheme', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ theme })})
            .then(() => {window.location.reload();});
        }
        function submitFeedback() {
            const feedback = document.getElementById("feedback").value;
            alert("Feedback submitted: " + feedback);
            document.getElementById("feedback").value = "";
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)