from flask import Flask, render_template_string, request, jsonify
import random

# Initialize Flask app
app = Flask(__name__)

# English responses dictionary
english_responses = {
    "hello": ["Hello!", "Hi there!", "Hey! How can I help you today?"],
    "how are you": ["I'm just a bot, but I'm doing great! How about you?", "I'm fine, thank you!"],
    "help": ["Sure! What do you need help with?", "I'm here to assist you."],
    "bye": ["Goodbye! Have a great day!", "See you later!", "Take care!"],
    "thank you": ["You're welcome!", "No problem at all!", "Happy to help!"]
}

# Malayalam responses dictionary
malayalam_responses = {
    "ഹലോ": ["ഹലോ!", "സുഖമാണോ?", "എനിക്ക് നിങ്ങളെ സഹായിക്കാൻ കഴിയും!"],
    "സുഖമാണോ": ["ഞാൻ ഒരു ബോട്ട് ആണ്, എനിക്ക് എല്ലാം സുഖമാണ്!", "നിങ്ങൾക്ക് സുഖമാണോ?"],
    "സഹായം": ["സഹായം ആവശ്യമുണ്ടോ? എന്ത് കാര്യമാണെന്ന് പറയൂ.", "ഞാൻ എപ്പോഴും സഹായിക്കാൻ തയ്യാറാണ്!"],
    "വിട": ["വിട, ശുഭദിനം!", "മറ്റൊരു ദിവസം കാണാം!", "ശുഭ ആശംസകൾ!"],
    "നന്ദി": ["സ്വാഗതം!", "അതിൽ പ്രശ്നമൊന്നുമില്ല!", "സഹായിക്കാൻ എനിക്ക് സന്തോഷമാണ്!"]
}

# Function to get a chatbot response
def get_chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # Check for responses in English
    for key, replies in english_responses.items():
        if key in user_input:
            return random.choice(replies)

    # Check for responses in Malayalam
    for key, replies in malayalam_responses.items():
        if key in user_input:
            return random.choice(replies)

    return "Sorry, I didn't understand that."

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
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f4f4f9;
        }
        .chat-container {
            width: 400px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-box {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            max-height: 400px;
            background: #e9ecef;
        }
        .message {
            margin: 5px 0;
            padding: 8px 12px;
            border-radius: 15px;
            max-width: 80%;
        }
        .message.user {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.bot {
            background: #dee2e6;
            color: black;
            margin-right: auto;
        }
        .input-container {
            display: flex;
            padding: 10px;
            background: #f8f9fa;
        }
        #user-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 16px;
        }
        #send-btn {
            padding: 10px 15px;
            margin-left: 10px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
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
        </div>
    </div>
    <script>
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        sendBtn.addEventListener('click', () => {
            const userMessage = userInput.value;
            if (!userMessage.trim()) return;

            // Display user message
            const userMessageDiv = document.createElement('div');
            userMessageDiv.className = 'message user';
            userMessageDiv.textContent = userMessage;
            chatBox.appendChild(userMessageDiv);

            // Clear input
            userInput.value = '';

            // Send message to the server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                // Display bot response
                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot';
                botMessageDiv.textContent = data.response;
                chatBox.appendChild(botMessageDiv);

                // Scroll to the bottom
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(err => console.error('Error:', err));
        });
    </script>
</body>
</html>
"""

# Route to serve the main page
@app.route('/')
def home():
    return render_template_string(html_template)

# API route to handle chatbot requests
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    bot_response = get_chatbot_response(user_message)
    return jsonify({'response': bot_response})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)