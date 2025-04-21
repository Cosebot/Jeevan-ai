from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"  # ← REPLACE WITH YOUR KEY
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    
    try:
        response = model.generate_content(message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

@app.route("/")
def serve_frontend():
    """Serves the chatbot UI"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sanji AI</title>
        <style>
            :root { --primary-color: #1b1f3b; --secondary-color: white; }
            body { 
                font-family: Arial, sans-serif; 
                background-color: var(--primary-color);
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                height: 100vh;
            }
            #chat-container {
                width: 90%;
                max-width: 400px;
                height: 60vh;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
                overflow-y: auto;
                margin-top: 20px;
                color: white;
            }
            .message { padding: 10px; margin: 10px 0; border-radius: 5px; max-width: 80%; }
            .user { background: white; margin-left: auto; color: black; }
            .bot { background: lightgreen; color: black; }
            .chat-input { 
                display: flex; 
                width: 90%; 
                max-width: 400px; 
                margin-top: 20px; 
            }
            input { flex: 1; padding: 10px; border-radius: 5px; border: none; }
            button { 
                background: var(--secondary-color); 
                color: var(--primary-color);
                border: none; 
                padding: 10px 20px; 
                margin-left: 10px; 
                border-radius: 5px; 
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="chat-container"></div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Type a message">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            function sendMessage() {
                const userInput = document.getElementById('user-input').value.trim();
                if (!userInput) return;

                const chatContainer = document.getElementById('chat-container');
                chatContainer.innerHTML += `<div class="message user">${userInput}</div>`;

                fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: userInput })
                })
                .then(response => response.json())
                .then(data => {
                    chatContainer.innerHTML += `<div class="message bot">${data.response}</div>`;
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                });

                document.getElementById('user-input').value = '';
            }

            // Enter key support
            document.getElementById('user-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });
        </script>
    </body>
    </html>
    ''')

if __name__ == "__main__":
    app.run(debug=True)