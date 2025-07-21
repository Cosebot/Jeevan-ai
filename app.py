import os import random import threading import time from flask import Flask, request, jsonify, send_file, render_template_string from gtts import gTTS import wikipedia from googleapiclient.discovery import build

app = Flask(name) app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default") app.permanent_session_lifetime = 365 * 24 * 60 * 60

Combined HTML, CSS, JS all in one file for inline rendering

chat_html = '''<!DOCTYPE html>

<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Sanji AI - Chat</title>
  <style>
    :root {
      --title-bg: #800020;
      --bg: #880808;
      --ai-bubble: #191970;
      --user-bubble: #A42A04;
      --input-bg: #A52A2A;
      --btn-bg: #1434A4;
      --text-color: white;
    }
    body {
      margin: 0;
      padding: 0;
      font-family: 'Bitcount Grid Single', sans-serif;
      background-color: var(--bg);
      color: var(--text-color);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    .title-box {
      background-color: var(--title-bg);
      text-align: center;
      padding: 10px;
      font-size: 1.4rem;
      font-weight: bold;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #transitionText {
      animation: switchText 6s infinite;
      transition: opacity 1s ease-in-out;
    }
    @keyframes switchText {
      0% { content: "Sanji AI"; opacity: 1; }
      49% { content: "Sanji AI"; opacity: 1; }
      50% { content: "Making your day better"; opacity: 0; }
      52% { opacity: 1; }
      100% { content: "Making your day better"; opacity: 1; }
    }
    .chat-container {
      flex: 1;
      padding: 10px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .chat-bubble {
      max-width: 80%;
      padding: 10px;
      border-radius: 10px;
      word-wrap: break-word;
    }
    .ai-bubble {
      background-color: var(--ai-bubble);
      align-self: flex-start;
    }
    .user-bubble {
      background-color: var(--user-bubble);
      align-self: flex-end;
    }
    .input-container {
      display: flex;
      padding: 10px;
      background-color: var(--input-bg);
      gap: 5px;
    }
    input[type="text"] {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 5px;
      font-family: 'Bitcount Grid Single', sans-serif;
    }
    button {
      padding: 10px;
      border: none;
      background-color: var(--btn-bg);
      color: white;
      border-radius: 5px;
      font-size: 1.1rem;
      font-family: 'Bitcount Grid Single', sans-serif;
    }
  </style>
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
  <script>
    const themes = [
      { name: "Spiderman", title: "#800020", bg: "#880808", ai: "#191970", user: "#A42A04", input: "#A52A2A", btn: "#1434A4" },
      { name: "Real Madrid", title: "#EDEADE", bg: "#87CEEB", ai: "#D22B2B", user: "#5D3FD3", input: "#FFD5EE", btn: "#FFAA33" },
      { name: "Zoro", title: "#097969", bg: "#50C878", ai: "#E4D00A", user: "#00A36C", input: "#0BDA51", btn: "#5D3FD3" },
      { name: "Cars", title: "#A7C7E7", bg: "#C2B280", ai: "#4682B4", user: "#D2042D", input: "#FF2400", btn: "#FDDA0D" },
      { name: "GTA SA", title: "#1B2121", bg: "#FFAC1C", ai: "#9F2B68", user: "#009E60", input: "#93C572", btn: "#E5E4E2" },
      { name: "Squid Game", title: "#36454F", bg: "#800020", ai: "#DC143C", user: "#478778", input: "#2AAA8A", btn: "#355E3B" }
    ];
    let currentTheme = 0;
    document.getElementById("theme-btn").addEventListener("click", () => {
      currentTheme = (currentTheme + 1) % themes.length;
      const theme = themes[currentTheme];
      document.documentElement.style.setProperty("--title-bg", theme.title);
      document.documentElement.style.setProperty("--bg", theme.bg);
      document.documentElement.style.setProperty("--ai-bubble", theme.ai);
      document.documentElement.style.setProperty("--user-bubble", theme.user);
      document.documentElement.style.setProperty("--input-bg", theme.input);
      document.documentElement.style.setProperty("--btn-bg", theme.btn);
    });
  </script>
</body>
</html>'''--- Chat Logic ---

english_responses = { "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help."], "how are you": ["Doing great! How about you?", "All systems go!"], "bye": ["Catch you later!", "Goodbye! Stay awesome!"], }

def get_chatbot_response(user_input, name=None): user_input = user_input.lower().strip() for key, responses in english_responses.items(): if key in user_input: response = random.choice(responses) return f"{name}, {response}" if name else response return f"{name}, I didn't understand that." if name else "Sorry, I didn't get that."

def detect_query_type(text): text = text.lower().strip() if text.startswith("who is") or "who is" in text: return "who" elif text.startswith("what is") or "what is" in text: return "what" elif text.startswith("where is") or "where is" in text: return "where" else: return "chat"

def extract_topic(text): text = text.lower() for keyword in ["play", "show me", "turn on", "video of"]: if keyword in text: return text.split(keyword, 1)[1].strip() return text.strip()

def search_wikipedia(query, sentences=2): try: summary = wikipedia.summary(query, sentences=sentences) return f"According to Wikipedia: {summary}" except wikipedia.DisambiguationError as e: return f"Too many results. Suggestions: {', '.join(e.options[:3])}" except wikipedia.PageError: return "Couldn't find anything." except Exception as e: return f"Error: {str(e)}"

def search_youtube_video(query): try: api_key = os.environ.get("YOUTUBE_API_KEY") youtube = build("youtube", "v3", developerKey=api_key) request = youtube.search().list(part="snippet", q=query, type="video", maxResults=1) response = request.execute() items = response.get("items") if items: video_id = items[0]["id"]["videoId"] title = items[0]["snippet"]["title"] return f'<iframe width="100%" height="315" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen></iframe><br>{title}' else: return "No video found." except Exception as e: return f"Error searching video: {str(e)}"

def cleanup_audio(*files): time.sleep(10) for file in files: if os.path.exists(file): os.remove(file)

@app.route("/") def index(): return render_template_string(chat_html)

@app.route("/chat", methods=["POST"]) def chat_post(): message = request.get_json().get("message", "") name = "" if any(keyword in message.lower() for keyword in ["play", "show me", "turn on", "video of"]): topic = extract_topic(message) response = search_youtube_video(topic) else: intent = detect_query_type(message) if intent in ["who", "what", "where"]: topic = extract_topic(message) response = search_wikipedia(topic) else: response = get_chatbot_response(message, name) return jsonify({"response": response})

@app.route("/speak", methods=["POST"]) def speak(): text = request.get_json().get("text", "") if not text: return jsonify({"error": "No text provided"}), 400 tts = gTTS(text=text, lang="en") filename = "temp.mp3" tts.save(filename) threading.Thread(target=cleanup_audio, args=(filename,)).start() return send_file(filename, mimetype="audio/mpeg")

@app.route("/setname", methods=["POST"]) def setname(): return jsonify({"status": "success"})

@app.route("/settheme", methods=["POST"]) def settheme(): return jsonify({"status": "success"})

if name == "main": app.run(debug=True)

