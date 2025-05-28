from flask import Flask, request, jsonify, redirect, session, render_template_string, send_file from gtts import gTTS import os, random, threading, time, wikipedia from supabase import create_client

app = Flask(name) app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default") app.permanent_session_lifetime = 365 * 24 * 60 * 60

Supabase

SUPABASE_URL = os.environ.get("SUPABASE_URL") SUPABASE_KEY = os.environ.get("SUPABASE_KEY") supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

Response logic

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

