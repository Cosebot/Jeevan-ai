from flask import Flask, render_template_string, request, jsonify
import random
import pyttsx3
import speech_recognition as sr

# Initialize Flask app
app = Flask(__name__)

# Initialize TTS engine
engine = pyttsx3.init()

# English responses dictionary
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"], 
"i am fine": ["Good to hear!", "Great man! ", " May god bless you!"]
}

# Malayalam responses dictionary
malayalam_responses = {
    "ഹലോ": ["ഹലോ!", "സുഖമാണോ?", "എനിക്ക് നിങ്ങളെ സഹായിക്കാൻ കഴിയും!"],
    "സുഖമാണോ? ": ["എനിക്ക്  സുഖമാണ്!", "നിങ്ങൾക്ക് സുഖമാണോ?"],
    "എന്നെ സഹായിക്കാമ്മോ?": ["സഹായം ആവശ്യമുണ്ടോ? എന്ത് കാര്യമാണെന്ന് പറയൂ.", "ഞാൻ എപ്പോഴും സഹായിക്കാൻ തയ്യാറാണ്!"],
    "പിന്നെ കാണാം": ["ഓക്കെ, ഷിഭുദിനം!", "പിന്നെ കാണാം!"],
    "നന്ദി": ["സ്വാഗതം!", "അതിൽ പ്രശ്നമൊന്നുമില്ല!", "സഹായിക്കാൻ എനിക്ക് സന്തോഷമാണ്!"], 
  എനിക്ക് സുഖമാണ്": [നല്ല കാര്യം!", "ആഹാ!", "ദൈവം അനുഗ്രഹിക്കട്ടേ!"]
}


# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # Check if the input is in English or Malayalam
    if any(word in user_input for word in english_responses.keys()):
        return random.choice(english_responses.get(user_input.lower(), ["Sorry, I didn't understand that."]))
    
    if any(word in user_input for word in malayalam_responses.keys()):
        return random.choice(malayalam_responses.get(user_input.lower(), ["ക്ഷമിക്കണം, എനിക്ക് അതു മനസ്സിലായില്ല."]))

    return "Sorry, I didn't understand that."

# Function to make the chatbot speak using pyttsx3 (Text-to-Speech)
def speak(text, language="en"):
    if language == "ml":  # Malayalam
        engine.setProperty('voice', 'com.apple.speech.synthesis.voice.millicent')  # Example voice for Malayalam
    else:  # Default to English
        engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
    
    engine.say(text)
    engine.runAndWait()

# Function to listen to the user's speech using SpeechRecognition (STT)
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, I couldn't request results from Google Speech Recognition service.")
            return None

# HTML, CSS, and JavaScript embedded in the Python script
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        /* Add the previous CSS styles here */
    </style>
</head>
<body>
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
    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        const voiceBtn = document.getElementById('voice-btn');

        sendBtn.addEventListener('click', () => {
            const userMessage = userInput.value;
            if (!userMessage.trim()) return;

            // Display user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'message user';
            userMessageDiv.textContent = userMessage;
            chatBox.appendChild(userMessageDiv);

            // Clear input field
            userInput.value = '';

            // Send message to Flask backend for response
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                // Display chatbot response
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot';
                botMessageDiv.textContent = data.response;
                chatBox.appendChild(botMessageDiv);
                
                // Trigger TTS to speak the response
                let language = "en";  // Default to English
                if (data.response.includes("സുഖമാണോ") || data.response.includes("എന്തെ?")) {
                    language = "ml";  // Malayalam
                }
                
                // Call TTS function to speak the response
                speak(data.response, language);
            });
        });

        voiceBtn.addEventListener('click', () => {
            // Start listening to user's voice input
            fetch('/listen', {
                method: 'GET'
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    userInput.value = data.message;
                    sendBtn.click();  // Automatically send the voice input
                }
            });
        });
    </script>
</body>
</html>
"""

# Route for the chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Route to listen to user voice input
@app.route('/listen', methods=['GET'])
def listen_to_user():
    message = listen()  # Listen for speech input
    if message:
        return jsonify({'message': message})
    else:
        return jsonify({'message': 'Sorry, I didn\'t understand that.'})

# Route for the main page (HTML)
@app.route('/')
def home():
    return render_template_string(html_template)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)