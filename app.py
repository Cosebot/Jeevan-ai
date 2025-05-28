from flask import Flask, request, jsonify, redirect, session, render_template_string
from gtts import gTTS
import os, random, threading, time, re, wikipedia
from googleapiclient.discovery import build
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-fallback")

# Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Simple chatbot logic
english_responses = {
    "hello": ["Hey there!", "Hi!", "Hello!"],
    "how are you": ["Doing well, thanks!", "I'm great! How about you?"],
    "bye": ["Goodbye!", "See you soon!"]
}

def get_response(msg):
    msg = msg.lower().strip()
    for key, responses in english_responses.items():
        if key in msg:
            return random.choice(responses)
    return "Sorry, I didn't get that."

def cleanup_audio(*files):
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

def search_wikipedia(query, sentences=2):
    try:
        return wikipedia.summary(query, sentences=sentences)
    except:
        return "Sorry, I couldn't find anything."

# ROUTES

@app.route("/")
def index():
    if "token" in session:
        return redirect("/chat")
    return render_template_string(landing_page_html)

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if result.get("error"):
        return render_template_string(landing_page_html, error="Login failed.")
    session["token"] = result["session"]["access_token"]
    return redirect("/chat")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form.get("email")
    password = request.form.get("password")
    result = supabase.auth.sign_up({"email": email, "password": password})
    if result.get("error"):
        return render_template_string(landing_page_html, error="Signup failed.")
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/chat")
def chat_page():
    if "token" not in session:
        return redirect("/")
    return render_template_string(chat_page_html)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "")
    if any(x in msg.lower() for x in ["who", "what", "where"]):
        reply = search_wikipedia(msg)
    else:
        reply = get_response(msg)
    return jsonify({"response": reply})

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


# === HTML Embedded Below ===

landing_page_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI</title>
    <style>
        body {
            background: #100018;
            color: #fff;
            font-family: Arial, sans-serif;
            text-align: center;
            padding-top: 10vh;
        }
        .form {
            margin-top: 2rem;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            border: none;
        }
        .section {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Elevate your thinking</h1>
    <p>Discover endless ways our AI can enhance your happiness, thinking, and companionship</p>

    <div class="form">
        <h2>Login</h2>
        <form action="/login" method="post">
            <input name="email" placeholder="Email" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>

        <div class="section">
            <h2>or Sign Up</h2>
            <form action="/signup" method="post">
                <input name="email" placeholder="Email" required><br>
                <input name="password" type="password" placeholder="Password" required><br>
                <button type="submit">Sign Up</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

chat_page_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI Chat</title>
    <style>
        body {
            background: #180030;
            color: #fff;
            font-family: Arial, sans-serif;
            padding: 10px;
        }
        #chat-box {
            background: #2a005f;
            border-radius: 10px;
            padding: 10px;
            height: 400px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .message {
            margin: 5px 0;
            padding: 8px;
            border-radius: 6px;
        }
        .user { background: #48ffb7; color: #000; text-align: right; }
        .bot { background: #8b2af7; color: #fff; text-align: left; }
        input {
            padding: 10px;
            width: 80%;
        }
        button {
            padding: 10px;
        }
    </style>
</head>
<body>
    <h2>Welcome to Sanji AI</h2>
    <div id="chat-box"></div>
    <input type="text" id="input" placeholder="Say something..." />
    <button onclick="send()">Send</button>
    <button onclick="logout()">Logout</button>

    <script>
        function send() {
            const input = document.getElementById("input");
            const message = input.value.trim();
            if (!message) return;
            document.getElementById("chat-box").innerHTML += `<div class='message user'>${message}</div>`;
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById("chat-box").innerHTML += `<div class='message bot'>${data.response}</div>`;
                input.value = "";
            });
        }
        function logout() {
            window.location.href = "/logout";
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)