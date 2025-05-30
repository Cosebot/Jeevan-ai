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
app.permanent_session_lifetime = 365 * 24 * 60 * 60

# ----- Chatbot Responses & Logic -----

english_responses = {
    "hello": ["Hey there!", "Hi!", "Hello!"],
    "how are you": ["Doing well, thanks!", "I'm great! How about you?"],
    "bye": ["Goodbye!", "See you soon!"]
}

def get_response(msg, name=None):
    msg = msg.lower().strip()
    for key, responses in english_responses.items():
        if key in msg:
            r = random.choice(responses)
            return f"{name}, {r}" if name else r
    return f"{name}, I didn't get that." if name else "Sorry, I didn't get that."

def cleanup_audio(*files):
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

def search_wikipedia(query, sentences=2):
    try:
        return wikipedia.summary(query, sentences=sentences)
    except wikipedia.DisambiguationError as e:
        return f"Too many results. Try to be more specific: {', '.join(e.options[:3])}"
    except wikipedia.PageError:
        return "Sorry, I couldn't find anything."
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
            return "Sorry, I couldn't find a video for that."
    except Exception as e:
        return f"Error searching video: {str(e)}"

# ----- Routes -----

@app.route("/")
def home():
    if "token" in session:
        return redirect("/chat")
    return redirect("/login")

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
                return redirect("/chat")
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

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "token" not in session:
        return redirect("/login")
    if request.method == "POST":
        msg = request.get_json().get("message", "")
        name = session.get("name", "")
        if any(x in msg.lower() for x in ["who", "what", "where"]):
            response = search_wikipedia(msg)
        else:
            response = get_response(msg, name)
        return jsonify({"response": response})
    return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

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
</head>
<body>
    <form method="POST">
        <input name="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sanji AI</title>
</head>
<body>
    <h2>Sanji AI</h2>
    <div id="chat-box"></div>
    <input id="input" placeholder="Type a message...">
    <button onclick="send()">Send</button>
    <script>
        function send() {
            const text = document.getElementById("input").value;
            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            })
            .then(res => res.json())
            .then(data => {
                const chat = document.getElementById("chat-box");
                const div = document.createElement("div");
                div.textContent = data.response;
                chat.appendChild(div);
            });
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)