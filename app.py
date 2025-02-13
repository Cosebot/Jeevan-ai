from flask import Flask, render_template, request, jsonify
import os
from gtts import gTTS
import speech_recognition as sr

app = Flask(__name__)

# Simple AI response logic
def chatbot_response(user_input):
    responses = {
        "hello": "Hi there!",
        "how are you": "I'm just a bot, but I'm doing fine!",
        "what's your name": "I'm Sanji AI, your assistant.",
        "bye": "Goodbye! Have a great day!",
        "default": "I'm still learning! Can you rephrase that?"
    }
    return responses.get(user_input.lower(), responses["default"])

# Home route serving the chatbot UI
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sanji AI</title>
        <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
                background-color: #1b1f3b;
                color: white;
                justify-content: center;
                margin: 0;
                width: 100vw;
                max-width: 430px;
            }
            #chat-box {
                width: 95%;
                max-width: 400px;
                height: 70vh;
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                overflow-y: auto;
                color: black;
            }
            .message {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                max-width: 80%;
            }
            .user { background-color: #e1f7d5; align-self: flex-end; text-align: right; }
            .bot { background-color: #d8e3fc; align-self: flex-start; text-align: left; }
            .chat-input {
                display: flex;
                align-items: center;
                background-color: white;
                border-radius: 30px;
                padding: 10px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                width: 90%;
                max-width: 500px;
                margin-top: 10px;
            }
            .icon-container {
                display: flex;
                justify-content: space-around;
                width: 100%;
                margin-top: 10px;
            }
            .icon-group {
                display: flex;
                flex-direction: column;
                align-items: center;
                font-size: 14px;
                cursor: pointer;
                background: #001F3F;
                color: white;
                padding: 12px;
                border-radius: 50px;
                width: 55px;
                height: 55px;
                justify-content: center;
            }
            .icon-group i { color: white; font-size: 20px; }
        </style>
    </head>
    <body>

        <div id="chat-box"></div>

        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Message">
        </div>

        <div class="icon-container">
            <div class="icon-group" id="voice-btn">
                <i class="fas fa-microphone"></i>
                <span>Mic</span>
            </div>
            <div class="icon-group" id="send-btn">
                <i class="fas fa-paper-plane"></i>
                <span>Send</span>
            </div>
        </div>

        <script>
            // Send message to backend
            $("#send-btn").click(() => {
                let userMessage = $("#user-input").val().trim();
                if (!userMessage) return;

                // Append user message
                $("#chat-box").append(`<div class="message user">${userMessage}</div>`);

                // Send message to Flask backend
                $.ajax({
                    url: "/chat",
                    method: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ message: userMessage }),
                    success: (response) => {
                        $("#chat-box").append(`<div class="message bot">${response.reply}</div>`);
                        let audio = new Audio(response.audio);
                        audio.play();
                    }
                });

                $("#user-input").val(""); // Clear input field
            });

            // Speech recognition (Voice Input)
            $("#voice-btn").click(() => {
                $.post("/speech", {}, (data) => {
                    $("#user-input").val(data.text);
                });
            });
        </script>

    </body>
    </html>
    '''

# Handle chat input & AI response
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = chatbot_response(user_message)

    # Convert text-to-speech (TTS)
    tts = gTTS(bot_reply, lang='en')
    tts.save("static/response.mp3")

    return jsonify({"reply": bot_reply, "audio": "/static/response.mp3"})

# Handle voice input (Speech Recognition)
@app.route('/speech', methods=['POST'])
def speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"text": "Sorry, I didn't catch that."})
        except sr.RequestError:
            return jsonify({"text": "Speech recognition service unavailable."})

if __name__ == '__main__':
    app.run(debug=True)