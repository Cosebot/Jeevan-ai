import os
import random
import threading
import time
from flask import Flask, request, jsonify, send_file, render_template_string
from gtts import gTTS
import wikipedia
from googleapiclient.discovery import build

# ----- Flask App Init -----
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default")
app.permanent_session_lifetime = 365 * 24 * 60 * 60  # 1 year

# ----- Templates -----
chat_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sanji AI</title>
  <style>
    body {
      background: {{theme_gradient}};
      color: white;
      font-family: Arial, sans-serif;
      text-align: center;
      padding: 20px;
    }
    #chat-box {
      width: 100%;
      height: 300px;
      border: 1px solid white;
      overflow-y: scroll;
      margin-bottom: 10px;
      padding: 10px;
      background-color: rgba(0, 0, 0, 0.3);
    }
    input, button {
      padding: 10px;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <h1>Welcome to Sanji AI</h1>
  <div id="chat-box"></div>
  <input type="text" id="message" placeholder="Type your message..." />
  <button onclick="sendMessage()">Send</button>
  <button onclick="speakMessage()">🔊</button>
  <script>
    async function sendMessage() {
      const message = document.getElementById("message").value;
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
      });
      const data = await res.json();
      const box = document.getElementById("chat-box");
      box.innerHTML += `<div><strong>You:</strong> ${message}</div>`;
      box.innerHTML += `<div><strong>Sanji AI:</strong> ${data.response}</div>`;
      document.getElementById("message").value = "";
    }
    async function speakMessage() {
      const message = document.getElementById("message").value;
      const res = await fetch("/speak", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: message })
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.play();
    }
  </script>
</body>
</html>
"""

settings_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Settings</title>
  <style>
    body {
      background: {{theme_gradient}};
      color: white;
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    select, input, button {
      padding: 10px;
      margin-top: 10px;
      font-size: 16px;
    }
  </style>
</head>
<body>
  <h1>Sanji AI Settings</h1>
  <label for="name">Your Name:</label>
  <input type="text" id="name" placeholder="Enter your name">
  <button onclick="saveName()">Save</button>

  <br><br>
  <label for="theme">Choose Theme:</label>
  <select id="theme">
    <option value="default">Default</option>
    <option value="cyan-purple">Cyber Glow</option>
    <option value="green-yellow">Toxic Slime</option>
    <option value="pink-orange">Retro Wave</option>
  </select>
  <button onclick="saveTheme()">Apply Theme</button>

  <script>
    async function saveName() {
      const name = document.getElementById("name").value;
      await fetch("/setname", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name })
      });
      alert("Name saved.");
    }
    async function saveTheme() {
      const theme = document.getElementById("theme").value;
      await fetch("/settheme", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme })
      });
      location.reload();
    }
  </script>
</body>
</html>
"""

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
    return render_template_string(chat_html, email="", theme_gradient=get_theme_gradient("default"))

@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template_string(chat_html, email="", theme_gradient=get_theme_gradient("default"))

@app.route("/chat", methods=["POST"])
def chat_post():
    message = request.get_json().get("message", "")
    name = ""
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
    return jsonify({"status": "success"})

@app.route("/settheme", methods=["POST"])
def settheme():
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
    return render_template_string(settings_html, email="", theme_gradient=get_theme_gradient("default"))

if __name__ == "__main__":
    app.run(debug=True)