from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"  # ← REPLACE WITH YOUR KEY
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro')

# Add explicit POST handler for root route
@app.route("/", methods=["GET"])
def serve_frontend():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Chatbot</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                background: #1a1a1a;
                color: white;
            }
            #chat-container {
                height: 60vh;
                border: 1px solid #444;
                padding: 20px;
                overflow-y: auto;
                margin-bottom: 20px;
                border-radius: 8px;
            }
            .message { 
                padding: 10px; 
                margin: 5px;
                border-radius: 5px;
                max-width: 80%;
            }
            .user { background: #444; margin-left: auto; }
            .bot { background: #2d2d2d; }
            input, button {
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #444;
                background: #333;
                color: white;
            }
        </style>
    </head>
    <body>
        <div i