import os
import random
import threading
import time
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

def cleanup_audio(file_path):
    time.sleep(10)
    if os.path.exists(file_path):
        os.remove(file_path)

def get_theme_gradient(theme):
    gradients = {
        "default": "radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%)",
        "cyan-purple": "linear-gradient(135deg, #00bcd4, #8e24aa)",
        "green-yellow": "linear-gradient(135deg, #8bc34a, #ffeb3b)",
        "pink-orange": "linear-gradient(135deg, #ff4081, #ff9100)"
    }
    return gradients.get(theme, gradients["default"])

# ----- Templates -----
login_html = """ ... (same as before) ... """
signup_html = """ ... (same as before) ... """
chat_html = """ ... (same as before) ... """

# ----- Routes -----
@app.route("/")
def index():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if result.session:
            session.permanent = True
            session["token"] = result.session.access_token
            session["email"] = email
            session["theme"] = "default"
            name_resp = supabase.table("user_memories").select("memory_value")\
                .eq("user_mail", email)\
                .eq("memory_type", "setting")\
                .eq("memory_key", "preferred_name")\
                .limit(1).execute()
            session["name"] = name_resp.data[0]["memory_value"] if name_resp.data else "User"
            return redirect("/chat")
    return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]
        result = supabase.auth.sign_up({"email": email, "password": password})
        if result.model_dump().get("error"):
            return render_template_string(signup_html)
        supabase.table("user_memories").insert({
            "user_mail": email,
            "memory_type": "setting",
            "memory_key": "preferred_name",
            "memory_value": username
        }).execute()
        return redirect("/login")
    return render_template_string(signup_html)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "token" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    if request.method == "GET":
        theme = get_theme_gradient(session.get("theme", "default"))
        return render_template_string(chat_html, email=session.get("email", ""), theme_gradient=theme)
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

@app.route("/update_username", methods=["POST"])
def update_username():
    if "token" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    email = session.get("email", "")
    data = request.get_json()
    username = data.get("username", "").strip()
    if not username:
        return jsonify({"error": "Username cannot be empty."}), 400
    supabase.table("user_memories").insert({
        "user_mail": email,
        "memory_type": "setting",
        "memory_key": "preferred_name",
        "memory_value": username
    }).execute()
    session["name"] = username
    return jsonify({"message": "Username updated successfully!"})

@app.route("/get_user_info")
def get_user_info():
    if "token" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    email = session.get("email", "")
    name = session.get("name", "User")
    return jsonify({"email": email, "name": name})

if __name__ == "__main__":
    app.run(debug=True)