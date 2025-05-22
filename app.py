from flask import Flask,request, jsonify, send_file, render_template_string
from gtts import gTTS
import os 
import random 
import threading
import time 
import speech_recognition as sr
import wikipedia
import re
from googleapiclient.discovery import build
from difflib import get_close_matches  # for fuzzy matching

app = Flask(__name__)
#Refined Chatbot Responses

english_responses = { "hello": ["Hello there! How can I assist you today?", "Hi! Need anything?", "Hey! I'm here to help.", "Yo! What brings you here?"], "hi": ["Hi!", "Hey there!", "What's up?", "Hiya!"], "hey": ["Hey! How can I help?", "Yo! Ready to chat?", "Hey hey! Let's go."], "good morning": ["Good morning! Ready to crush the day?", "Morning! How can I help today?"], "good afternoon": ["Good afternoon! What's on your mind?", "Hey! How’s your day going?"], "good evening": ["Good evening! How was your day?", "Evening! I'm here if you need anything."], "good night": ["Good night! Catch you tomorrow.", "Sweet dreams!"],

"how are you": ["Doing great! How about you?", "All systems go! You?"],
"what's up": ["Just chilling in the digital world. You?", "Processing data and waiting for you!"] ,

"bye": ["Catch you later!", "Goodbye! Stay awesome!"],
"goodbye": ["Take care!", "See you soon!"],
"see you": ["Until next time!", "Bye for now!"] ,

"thank you": ["You're welcome!", "Anytime!", "Glad to help!"],
"thanks": ["You're welcome!", "No problem!"] ,

"who are you": ["I'm Sanji AI, your personal assistant.", "Call me Sanji, your digital buddy."],
"what is your name": ["Sanji AI, at your service!"],
"who made you": ["I was built by Ashkar – a genius, no doubt!"],
"where are you from": ["Straight outta cyberspace!", "I live in the cloud – literally!"] ,

"what can you do": ["I can chat, help with questions, fetch info, and even talk back!", "Your virtual assistant for info, laughs, and support."],
"can you learn": ["I don’t learn on my own just yet, but I get updates!"],
"can you think": ["I think fast, but not quite like humans – yet."],

"tell me a joke": [
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What do you call fake spaghetti? An impasta!",
    "Why don’t skeletons fight each other? They don’t have the guts!"
],
"tell me a fact": [
    "Did you know honey never spoils?",
    "Bananas are berries, but strawberries aren't!",
    "Octopuses have three hearts!"
],

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

#The rest of the logic remains unchanged...
def get_chatbot_response(user_input: str) -> str:
    """Simple chatbot logic"""
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

# Channel name to Live URL mapping
live_channel_urls = {
    "manorama news live": "https://www.youtube.com/live/tgBTspqA5nY?si=r_SP8Mddodothi0d",
    "24 news live": "https://www.youtube.com/live/1wECsnGZcfc?si=hY_UJTuZBHh8SARp",
    "mediaone news live": "https://www.youtube.com/live/-8d8-c0yvyU?si=9yJbKZK9b0K6PMVr",
    "mathrubhumi news live": "https://www.youtube.com/live/YGEgelAiUf0?si=2hrOUnI7_gOIVJTq",
    "reporter tv live": "https://www.youtube.com/live/HGOiuQUwqEw?si=fYvJLdLq0PWuY0Vi",
    "asianet news live": "https://www.youtube.com/live/Ko18SgceYX8?si=A5g587PmOOfACiL2"
}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower().strip()
# Video intent
    if message.startswith("play ") or message.startswith("show me ") or message.startswith("turn on "):
        topic = message.replace("play ", "").replace("show me ", "").replace("turn on ", "").strip()

        # Try fuzzy match for live channels
        possible_matches = get_close_matches(topic, live_channel_urls.keys(), n=1, cutoff=0.6)
        
        if possible_matches:
            best_match = possible_matches[0]
            url = live_channel_urls[best_match]
            response_text = f'<iframe width="100%" height="315" src="{url.replace("watch?v=", "embed/").split("?")[0]}" frameborder="0" allowfullscreen></iframe><br>Streaming {best_match.title()}'
        else:
            response_text = search_youtube_video(topic)
    else:
        # Detect type of question
        intent = detect_query_type(message)
        if intent in ["who", "what", "where"]:
            topic = extract_topic(message)
            response_text = search_wikipedia(topic)
        else:
            response_text = get_chatbot_response(message)

    return jsonify({"response": response_text})
@app.route("/speak", methods=["POST"])
def speak():
    """Converts chatbot response to speech"""
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)

    # Cleanup after 10 seconds
    threading.Thread(target=cleanup_audio, args=(filename,)).start()

    return send_file(filename, mimetype="audio/mpeg")

def cleanup_audio(*files):
    """Deletes temp audio files after 10 seconds"""
    time.sleep(10)
    for file in files:
        if os.path.exists(file):
            os.remove(file)

def search_youtube_video(query):
    try:
        api_key = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )
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

@app.route("/")
def serve_frontend():
    """Serves the chatbot UI with 10 color themes"""
    html_content = """
  <!DOCTYPE html><html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Sanji AI</title>
  <link href="https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary-color: #0E0307;
      --secondary-color: #6E33B1;
      --accent-color: #38E6A2;
      --bot-message-bg: #COB4E3;
      --user-message-bg: #EEEBF3;
      --text-color: #FFFFFF;
    }body {
  margin: 0;
  font-family: 'SF Pro Display', sans-serif;
  background: radial-gradient(circle at top, #6E33B1, #0E0307);
  color: var(--text-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100vh;
  justify-content: center;
}

#chat-container {
  width: 90%;
  max-width: 420px;
  height: 60vh;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 15px;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(206, 180, 227, 0.3);
}

.message {
  padding: 12px 16px;
  margin: 10px 0;
  border-radius: 20px;
  max-width: 80%;
  font-size: 15px;
}

.user {
  background: var(--user-message-bg);
  color: #000;
  align-self: flex-end;
}

.bot {
  background: var(--bot-message-bg);
  color: #000;
  align-self: flex-start;
}

.chat-input {
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 10px;
  width: 90%;
  max-width: 500px;
  margin-top: 20px;
  box-shadow: 0 0 10px #6E33B1;
}

.chat-input input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px;
  font-size: 16px;
  background: transparent;
  color: white;
}

.chat-input button {
  background: linear-gradient(145deg, #6E33B1, #COB4E3);
  color: white;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  padding: 10px 15px;
  margin-left: 10px;
  box-shadow: 0 0 10px #6E33B1;
  cursor: pointer;
}

.menu-container {
  position: absolute;
  top: 15px;
  right: 15px;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: var(--accent-color);
  cursor: pointer;
}

.menu-dropdown {
  display: none;
  position: absolute;
  top: 40px;
  right: 0;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 10px;
  border-radius: 10px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
}

.menu-dropdown.active {
  display: block;
}

.theme-btn {
  background: #6E33B1;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 6px 10px;
  border-radius: 8px;
  margin-top: 5px;
  width: 100%;
}

  </style>
</head>
<body>
  <div class="menu-container">
    <button class="menu-btn" onclick="toggleMenu()">⚙️</button>
    <div class="menu-dropdown" id="themeMenu"></div>
  </div>  <div id="chat-container"></div>  <div class="chat-input">
    <input type="text" id="user-input" placeholder="Type a message" />
    <button onclick="sendMessage()">Send</button>
    <button onclick="startVoiceInput()">🎙️</button>
  </div>  <script>
    const themes = [
      { name: "Glitch Effect", primary: "#6E33B1", secondary: "#COB4E3" },
      { name: "Neon Pulse", primary: "#38E6A2", secondary: "#6E33B1" },
      { name: "Cyber Light", primary: "#EEEBF3", secondary: "#0E0307" }
    ];

    function toggleMenu() {
      document.querySelector(".menu-dropdown").classList.toggle("active");
    }

    function applyTheme(primary, secondary) {
      document.documentElement.style.setProperty('--primary-color', primary);
      document.documentElement.style.setProperty('--secondary-color', secondary);
    }

    function sendMessage() {
      const userInput = document.getElementById('user-input').value.trim();
      if (!userInput) return;
      const chatContainer = document.getElementById('chat-container');
      chatContainer.innerHTML += `<div class='message user'>${userInput}</div>`;

      fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput })
      })
      .then(res => res.json())
      .then(data => {
        chatContainer.innerHTML += `<div class='message bot'>${data.response}</div>`;
        if (!data.response.includes("<iframe")) {
          fetch('/speak', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: data.response })
          })
          .then(res => res.blob())
          .then(blob => new Audio(URL.createObjectURL(blob)).play());
        }
      });

      document.getElementById('user-input').value = '';
    }

    function startVoiceInput() {
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = "en-US";
      recognition.onresult = event => {
        document.getElementById("user-input").value = event.results[0][0].transcript;
      };
      recognition.start();
    }

    const menu = document.getElementById("themeMenu");
    themes.forEach(theme => {
      const btn = document.createElement("button");
      btn.className = "theme-btn";
      btn.textContent = theme.name;
      btn.onclick = () => applyTheme(theme.primary, theme.secondary);
      menu.appendChild(btn);
    });
  </script> 
</body>
</html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)