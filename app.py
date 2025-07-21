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

# ----- Replacing GUI with custom HTML -----
chat_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Sanji AI - Chat</title>

  <!-- Font and Styles -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bitcount+Grid+Single:wght@100..900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css" />
</head>

<body>
  <div class="title-box">
    <span id="transitionText">Sanji AI</span>
  </div>

  <div class="chat-container" id="chat-container">
    <div class="chat-bubble ai-bubble">Hello! I’m Sanji AI</div>
    <div class="chat-bubble user-bubble">Yo!</div>
  </div>

  <div class="input-container">
    <input type="text" id="user-input" placeholder="Say something..." />
    <button id="send-btn">➤</button>
    <button id="theme-btn">🎨</button>
  </div>

  <script src="script.js"></script>
</body>
</html>'''

# Settings HTML untouched
settings_html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
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
  <label for=\"name\">Your Name:</label>
  <input type=\"text\" id=\"name\" placeholder=\"Enter your name\">
  <button onclick=\"saveName()\">Save</button>

  <br><br>
  <label for=\"theme\">Choose Theme:</label>
  <select id=\"theme\">
    <option value=\"default\">Default</option>
    <option value=\"cyan-purple\">Cyber Glow</option>
    <option value=\"green-yellow\">Toxic Slime</option>
    <option value=\"pink-orange\">Retro Wave</option>
  </select>
  <button onclick=\"saveTheme()\">Apply Theme</button>

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
</html>"""

# The rest of the logic (routes, chat, speak) remains untouched...

@app.route("/")
def index():
    return render_template_string(chat_html)

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
    return render_template_string(settings_html, email="", theme_gradient="radial-gradient(circle at top, #0E0307 0%, #1b0b2e 100%)")

if __name__ == "__main__":
    app.run(debug=True)
