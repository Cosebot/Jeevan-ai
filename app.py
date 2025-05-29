# ----- Imports -----
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

# ----- Supabase Auth Init -----
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#Response logic

english_responses = { "hello": ["Hey there!", "Hi!", "Hello!"], "how are you": ["Doing well, thanks!", "I'm great! How about you?"], "bye": ["Goodbye!", "See you soon!"] }

def get_response(msg, name=None): msg = msg.lower().strip() for key, responses in english_responses.items(): if key in msg: r = random.choice(responses) return f"{name}, {r}" if name else r return f"{name}, I didn't get that." if name else "Sorry, I didn't get that."

def cleanup_audio(*files): time.sleep(10) for file in files: if os.path.exists(file): os.remove(file)

def search_wikipedia(query, sentences=2): try: return wikipedia.summary(query, sentences=sentences) except: return "Sorry, I couldn't find anything."

@app.route("/") def home(): if "token" in session: return redirect("/chat") return redirect("/login")

@app.route("/login", methods=["GET", "POST"]) def login(): if request.method == "POST": email = request.form["email"] password = request.form["password"] try: result = supabase.auth.sign_in_with_password({"email": email, "password": password}) if result.session: session.permanent = True session["token"] = result.session.access_token session["email"] = email session["name"] = "" return redirect("/chat") return render_template_string(login_html, error="Login failed.") except: return render_template_string(login_html, error="Invalid credentials.") return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"]) def signup(): if request.method == "POST": email = request.form["email"] password = request.form["password"] result = supabase.auth.sign_up({"email": email, "password": password}) if result.model_dump().get("error"): return render_template_string(signup_html, error="Signup failed.") return redirect("/login") return render_template_string(signup_html)

@app.route("/logout") def logout(): session.clear() return redirect("/login")

@app.route("/chat", methods=["GET", "POST"]) def chat(): if "token" not in session: return redirect("/login") if request.method == "POST": msg = request.get_json().get("message", "") name = session.get("name", "") if any(x in msg.lower() for x in ["who", "what", "where"]): response = search_wikipedia(msg) else: response = get_response(msg, name) return jsonify({"response": response}) return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

@app.route("/setname", methods=["POST"]) def setname(): data = request.get_json() session["name"] = data.get("name", "") return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

----------------- HTML Templates ------------------

login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)

# ----- Flask App Init -----
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default")
app.permanent_session_lifetime = 365 * 24 * 60 * 60

# ----- Chatbot Responses & Logic -----
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

# ----- Wikipedia Search -----
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

# ----- YouTube Search -----
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

# ----- Audio Speak Route -----


# ----- Cleanup -----
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

# ----- Auth Routes -----
@app.route("/login", methods=["GET", "POST"]) def login(): if request.method == "POST": email = request.form["email"] password = request.form["password"] try: result = supabase.auth.sign_in_with_password({"email": email, "password": password}) if result.session: session.permanent = True session["token"] = result.session.access_token session["email"] = email session["name"] = "" return redirect("/chat") return render_template_string(login_html, error="Login failed.") except: return render_template_string(login_html, error="Invalid credentials.") return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"]) def signup(): if request.method == "POST": email = request.form["email"] password = request.form["password"] result = supabase.auth.sign_up({"email": email, "password": password}) if result.model_dump().get("error"): return render_template_string(signup_html, error="Signup failed.") return redirect("/login") return render_template_string(signup_html)

@app.route("/logout") def logout(): session.clear() return redirect("/login")

@app.route("/chat", methods=["GET", "POST"]) def chat(): if "token" not in session: return redirect("/login") if request.method == "POST": msg = request.get_json().get("message", "") name = session.get("name", "") if any(x in msg.lower() for x in ["who", "what", "where"]): response = search_wikipedia(msg) else: response = get_response(msg, name) return jsonify({"response": response}) return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

@app.route("/setname", methods=["POST"]) def setname(): data = request.get_json() session["name"] = data.get("name", "") return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

----------------- HTML Templates ------------------

login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)
@app.route("/signup", methods=["GET", "POST"]) def signup(): if request.method == "POST": email = request.form["email"] password = request.form["password"] result = supabase.auth.sign_up({"email": email, "password": password}) if result.model_dump().get("error"): return render_template_string(signup_html, error="Signup failed.") return redirect("/login") return render_template_string(signup_html)

@app.route("/logout") def logout(): session.clear() return redirect("/login")

@app.route("/chat", methods=["GET", "POST"]) def chat(): if "token" not in session: return redirect("/login") if request.method == "POST": msg = request.get_json().get("message", "") name = session.get("name", "") if any(x in msg.lower() for x in ["who", "what", "where"]): response = search_wikipedia(msg) else: response = get_response(msg, name) return jsonify({"response": response}) return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

@app.route("/setname", methods=["POST"]) def setname(): data = request.get_json() session["name"] = data.get("name", "") return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

----------------- HTML Templates ------------------

login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)
@app.route("/logout") def logout(): session.clear() return redirect("/login")

@app.route("/chat", methods=["GET", "POST"]) def chat(): if "token" not in session: return redirect("/login") if request.method == "POST": msg = request.get_json().get("message", "") name = session.get("name", "") if any(x in msg.lower() for x in ["who", "what", "where"]): response = search_wikipedia(msg) else: response = get_response(msg, name) return jsonify({"response": response}) return render_template_string(chat_html, email=session.get("email", ""), name=session.get("name", ""))

@app.route("/setname", methods=["POST"]) def setname(): data = request.get_json() session["name"] = data.get("name", "") return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

----------------- HTML Templates ------------------

login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)
@app.route("/setname", methods=["POST"]) def setname(): data = request.get_json() session["name"] = data.get("name", "") return jsonify({"status": "success"})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

----------------- HTML Templates ------------------

login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)

# ----- Chat Route -----


# ----- Homepage -----
@app.route("/")
def home():
    if "token" in session:
        return redirect("/chat")
    return redirect("/login")

# ----- HTML Templates -----
login_html = """

<!DOCTYPE html><html><head><title>Login</title><style>body { background: #0a0116; color: #fff; font-family: sans-serif; margin: 0; height: 100vh; display: flex; align-items: center; justify-content: center; } form { width: 90%; max-width: 400px; display: flex; flex-direction: column; gap: 15px; } input, button { padding: 15px; border-radius: 10px; border: none; font-size: 16px; } button { background: #6E33B1; color: #fff; } a { color: #48ffb7; text-align: center; font-size: 14px; } </style></head><body>

<form method="POST">
  <h2 style="text-align:center;">Login to Sanji AI</h2>
  <input name="email" type="email" placeholder="Email" required>
  <input name="password" type="password" placeholder="Password" required>
  <button type="submit">Login</button>
  <div style="text-align:center;">New user? <a href="/signup">Create an account</a></div>
</form>
</body></html>
"""signup_html = login_html.replace("Login", "Sign Up").replace("/login", "/signup").replace("Login to", "Create a")

chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)
chat_html = """

<!DOCTYPE html><html><head><title>Sanji AI</title><style>body { background: #0a0116; color: white; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; } #chat-box { flex: 1; overflow-y: auto; margin: 10px; padding: 10px; border-radius: 10px; background: #1b0b2e; } .message { margin: 10px 0; padding: 10px; border-radius: 10px; } .user { background: #48ffb7; color: black; text-align: right; } .bot { background: #6E33B1; color: white; text-align: left; } .input-bar { display: flex; padding: 10px; } input { flex: 1; padding: 12px; border-radius: 30px; border: none; } button { padding: 12px; margin-left: 5px; border-radius: 30px; background: #8a2be2; color: white; border: none; } #menu { position: absolute; top: 15px; right: 15px; } #dropdown { display: none; position: absolute; right: 15px; top: 60px; background: #1b0b2e; border-radius: 10px; padding: 10px; z-index: 1; } #dropdown input { width: 90%; margin-top: 5px; } </style></head><body>

<div id="menu">
  <button onclick="toggleDropdown()">☰</button>
  <div id="dropdown">
    <p><b>{{ email }}</b></p>
    <button onclick="logout()">Logout</button>
    <hr><label>Name:</label>
    <input id="nameInput" placeholder="Your name" value="{{ name }}">
    <button onclick="saveName()">Save</button>
  </div>
</div>
<h2 style="text-align:center;">Sanji AI</h2>
<div id="chat-box"></div>
<div class="input-bar">
  <input id="input" placeholder="Type a message...">
  <button onclick="send()">Send</button>
</div>
<script>
function toggleDropdown() {
  const d = document.getElementById("dropdown");
  d.style.display = d.style.display === "block" ? "none" : "block";
}
function logout() { window.location = "/logout"; }
function saveName() {
  const name = document.getElementById("nameInput").value;
  fetch("/setname", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name })
  });
}
function send() {
  const input = document.getElementById("input");
  const text = input.value.trim();
  if (!text) return;
  const chat = document.getElementById("chat-box");
  chat.innerHTML += `<div class='message user'>${text}</div>`;
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
  .then(res => res.json())
  .then(data => {
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    if (data.response.includes("<iframe")) {
      botDiv.innerHTML = data.response;
    } else {
      botDiv.textContent = data.response;
    }
    chat.appendChild(botDiv);
    input.value = "";
    chat.scrollTop = chat.scrollHeight;
  });
}
</script></body></html>
"""if name == "main": app.run(debug=True)

# ----- Run Server -----
if __name__ == "__main__":
    app.run(debug=True)