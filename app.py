from flask import Flask, request, jsonify, send_file, render_template_string, render_template, redirect, session
from gtts import gTTS
import os 
import random 
import threading
import time 
import speech_recognition as sr
import wikipedia
import re
from googleapiclient.discovery import build
from supabase import create_client

app = Flask(__name__)

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower().strip()

    if message.startswith("play ") or message.startswith("show me ") or message.startswith("turn on "):
        topic = message.split(" ", 1)[1]
        response_text = search_youtube_video(topic)
    else:
        intent = detect_query_type(message)
        if intent in ["who", "what", "where"]:
            topic = extract_topic(message)
            response_text = search_wikipedia(topic)
        else:
            response_text = get_chatbot_response(message)

    return jsonify({"response": response_text})

@app.route("/auth")
def auth_page():
    return render_template("auth.html")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    name = request.form["name"]
    result = supabase.auth.sign_up({"email": email, "password": password})
    if result.get("error"):
        return f"Signup Error: {result['error']['message']}"
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    result = supabase.auth.sign_in_with_password({"email": email, "password": password})
    if result.get("error"):
        return f"Login Error: {result['error']['message']}"
    session["token"] = result["session"]["access_token"]
    return redirect("/")

@app.route("/")
def serve_frontend():
    with open("SanjiAIsourcecode.txt", "r") as f:
        return render_template_string(f.read())

if __name__ == "__main__":
    app.run(debug=True)
