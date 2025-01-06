from flask import Flask, render_template_string, request, jsonify, send_file
from gtts import gTTS
import os
import platform
import random

# Initialize Flask app
app = Flask(__name__)

# English responses dictionary
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"], 
    "i am fine": ["Good to hear!", "Great man! ", " May god bless you!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()

    if any(word in user_input for word in english_responses.keys()):
        return random.choice(english_responses.get(user_input.lower(), ["Sorry, I didn't understand that."]))

    return "Sorry, I didn't understand that."

# Function to make the chatbot speak using gTTS (Google Text-to-Speech)
def speak(text, language="en"):
    # Generate speech with Google TTS
    tts = gTTS(text=text, lang=language)
    tts.save("response.mp3")  # Save the speech as an MP3 file

    # Platform-specific commands to play the MP3 file
    current_platform = platform.system().lower()

    if current_platform == "windows":
        os.system("start response.mp3")  # Windows command
    elif current_platform == "darwin":  # macOS
        os.system("afplay response.mp3")  # macOS command
    elif current_platform == "linux" or current_platform == "linux2":
        os.system("mpg321 response.mp3")  # Linux command (ensure mpg321 is installed)
    else:
        print("Platform not supported for automatic audio playback.")

# Route for the chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Route to serve the audio file to the client for playback
@app.route('/speak', methods=['GET'])
def speak_text():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')
    tts = gTTS(text=text, lang=language)
    
    # Save the MP3 in a temporary file
    temp_mp3_path = "response.mp3"
    tts.save(temp_mp3_path)
    
    # Serve the MP3 file as a response
    return send_file(temp_mp3_path, mimetype='audio/mpeg', as_attachment=False)

# HTML, CSS, and JavaScript embedded in the Python script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .chat-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
        }
        .chat-box {
            flex-grow: 1;
            padding: 10px;
            overflow-y: auto;
            max-height: 80%;
            background-color: var(--background-color);
        }
        .input-container {
            display: flex;
            padding: 10px;
            background-color: var(--background-color);
        }
        #user-input {
            flex-grow: 1;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid var(--text-color);
            background-color: var(--input-bg-color);
            color: var(--text-color);
        }
        button {
            background-color: var(--button-bg-color);
            color: var(--button-text-color);
            padding: 10px;
            margin-left: 10px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        .message {
            margin: 5px 0;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
            color: var(--text-color);
        }
        .user {
            background-color: var(--user-bg-color);
            align-self: flex-end;
        }
        .bot {
            background-color: var(--bot-bg-color);
            align-self: flex-start;
        }
        .theme-selector {
            display: flex;
            justify-content: center;
            padding: 10px;
            background-color: var(--background-color);
        }
        .theme-selector button {
            margin: 5px;
            padding: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .theme-selector .diamond { background-color: lightblue; }
        .theme-selector .sakura { background-color: pink; }
        .theme-selector .gold { background-color: yellow; }
        .theme-selector .cloud { background-color: white; color: black; }
        .theme-selector .ant { background-color: black; color: white; }

        .contact-us {
            padding: 20px;
            background-color: var(--background-color);
            text-align: center;
            border-top: 1px solid var(--text-color);
        }
        .contact-us p {
            margin: 5px 0;
            color: var(--text-color);
        }
        .contact-us a {
            color: var(--button-bg-color);
            text-decoration: none;
            font-weight: bold;
        }
        .contact-us a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="theme-selector">
        <button class="diamond" onclick="setTheme('diamond')">Diamond</button>
        <button class="sakura" onclick="setTheme('sakura')">Sakura</button>
        <button class="gold" onclick="setTheme('gold')">Gold</button>
        <button class="cloud" onclick="setTheme('cloud')">Cloud</button>
        <button class="ant" onclick="setTheme('ant')">Ant</button>
    </div>

    <div class="chat-container">
        <div id="chat-box" class="chat-box">
            <!-- Chat messages will appear here -->
        </div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type your message here..." />
            <button id="send-btn">Send</button>
            <button id="voice-btn">🎤 Speak</button>
        </div>
    </div>

    <div class="contact-us">
        <p>CEO and Main Admin of Bot</p>
        <p><a href="mailto:hazanulashkar@gmail.com">hazanulashkar@gmail.com</a></p>
    </div>

    <script>
        // Theme colors
        const themes = {
            diamond: {
                '--background-color': 'lightblue',
                '--text-color': '#000',
                '--button-bg-color': '#0056b3',
                '--button-text-color': '#fff',
                '--input-bg-color': '#e0f7fa',
                '--user-bg-color': '#0288d1',
                '--bot-bg-color': '#b3e5fc'
            },
            sakura: {
                '--background-color': 'pink',
                '--text-color': '#000',
                '--button-bg-color': '#ad1457',
                '--button-text-color': '#fff',
                '--input-bg-color': '#f8bbd0',
                '--user-bg-color': '#880e4f',
                '--bot-bg-color': '#f48fb1'
            },
            gold: {
                '--background-color': 'yellow',
                '--text-color': '#000',
                '--button-bg-color': '#f57f17',
                '--button-text-color': '#fff',
                '--input-bg-color': '#fff9c4',
                '--user-bg-color': '#ffab00',
                '--bot-bg-color': '#ffe082'
            },
            cloud: {
                '--background-color': 'white',
                '--text-color': '#000',
                '--button-bg-color': '#607d8b',
                '--button-text-color': '#fff',
                '--input-bg-color': '#f5f5f5',
                '--user-bg-color': '#cfd8dc',
                '--bot-bg-color': '#eceff1'
            },
            ant: {
                '--background-color': 'black',
                '--text-color': '#fff',
                '--button-bg-color': '#424242',
                '--button-text-color': '#fff',
                '--input-bg-color': '#616161',
                '--user-bg-color': '#757575',
                '--bot-bg-color': '#9e9e9e'
            }
        };

        // Function to apply a theme
        function setTheme(themeName) {
            const theme = themes[themeName];
            for (const property in theme) {
                document.documentElement.style.setProperty(property, theme[property]);
            }
        }

        // Default theme
        setTheme('diamond');
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(debug=True)