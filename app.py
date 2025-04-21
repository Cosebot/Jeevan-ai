from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API (replace with your API key)
GOOGLE_API_KEY = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"
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
    """Serves the same chatbot UI"""
    html_content = """
    <!DOCTYPE html>
<html>
<head>
    <!-- Same HTML and CSS as original -->
    <style>
        /* Same CSS styles as original */
    </style>
</head>
<body>
    <!-- Same HTML structure as original -->
    <script>
        // Same JavaScript as original except remove speech functions
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
            .then(response => response.json())
            .then(data => {
                chatContainer.innerHTML += `<div class='message bot'>${data.response}</div>`;
            });

            document.getElementById('user-input').value = '';
        }

        // Rest of the theme switching code remains same
    </script>
</body>
</html>
    """
    return render_template_string(html_content)

if __name__ == "__main__":
    app.run(debug=True)