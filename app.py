from flask import Flask, request, jsonify, redirect, session, render_template_string, send_file
from gtts import gTTS
import os, random, threading, time, wikipedia
from googleapiclient.discovery import build
from supabase import create_client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback")

# Supabase

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Responses
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
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if result.model_dump().get("error"):
            return render_template_string(login_html, error="Login failed.")
        session["token"] = result.session.access_token
        return redirect("/chat")
    return render_template_string(login_html)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        result = supabase.auth.sign_up({"email": email, "password": password})

        # ✅ Safely check if there’s an error
        if result.model_dump().get("error"):
            return render_template_string(signup_html, error="Signup failed.")

        # ✅ Only set session if returned (when email confirmation is OFF)
        if result.session:
            session["token"] = result.session.access_token
            return redirect("/chat")

        # ✅ User created, but needs to verify email
        return render_template_string(login_html, error="Check your email to confirm your account.")
    
    return render_template_string(signup_html)

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

# HTML templates (mobile-optimized)

login_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Sanji AI</title>
    <style>
        body { background: #0a0116; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        input, button { width: 80%; max-width: 300px; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; font-size: 16px; }
        button { background: #6E33B1; color: #fff; }
        a { color: #48ffb7; text-decoration: none; }
        .container { text-align: center; width: 100%; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Login to Sanji AI</h2>
        <form method="POST">
            <input name="email" type="email" placeholder="Email" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
        <p>New user? <a href="/signup">Create an account</a></p>
    </div>
</body>
</html>
"""

signup_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sign Up - Sanji AI</title>
    <style>
        body { background: #0a0116; color: #fff; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        input, button { width: 80%; max-width: 300px; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; font-size: 16px; }
        button { background: #6E33B1; color: #fff; }
        a { color: #48ffb7; text-decoration: none; }
        .container { text-align: center; width: 100%; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Create a Sanji AI Account</h2>
        <form method="POST">
            <input name="email" type="email" placeholder="Email" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <button type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <a href="/login">Log in</a></p>
    </div>
</body>
</html>
"""

chat_html = """
<!DOCTYPE html>
<html>
  <body style="background:#111;color:white;font-family:sans-serif;text-align:center;padding-top:40vh;">
    <h1>✅ Chat route is working</h1>
    <p>If you see this, Flask is rendering the page correctly.</p>
    <a href='/logout' style='color:#48ffb7;'>Logout</a>
  </body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)