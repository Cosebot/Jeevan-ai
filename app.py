import requests
from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)

def search_duckduckgo(query):
    """Fetches the first 1000 characters from a DuckDuckGo search result."""
    search_url = f"https://lite.duckduckgo.com/lite?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result-link")
        
        if results:
            first_result = results[0].text.strip()  # Extract text
            article_link = "https://duckduckgo.com/?q=" + query.replace(" ", "+")
            return first_result[:1000], article_link  # Return first 1000 characters
        
    return "No relevant information found.", ""

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/ask', methods=['GET'])
def ask_chatbot():
    """Processes user input and returns the first 1000 characters + a link."""
    user_input = request.args.get('query', '').strip().lower()
    
    if any(user_input.startswith(word) for word in ["what", "where", "why", "how", "when"]):
        search_results, article_link = search_duckduckgo(user_input)
        return jsonify({"message": search_results, "link": article_link})
    
    return jsonify({"message": "I only answer questions starting with What/Where/Why/How/When."})

# HTML, CSS, and JS for the Chatbot UI
HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>DuckDuckGo AI Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #1e1e1e; color: #fff; }
        #chatbox { width: 60%; height: 400px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin: auto; background: #333; color: #fff; border-radius: 10px; }
        #userInput { width: 60%; padding: 10px; margin-top: 10px; background: #444; color: #fff; border: 1px solid #666; border-radius: 5px; }
        #sendBtn { padding: 10px; background: #ff9900; border: none; color: #fff; cursor: pointer; border-radius: 5px; }
        a { color: #ff9900; text-decoration: none; }
    </style>
</head>
<body>
    <h2>DuckDuckGo AI Chatbot</h2>
    <div id="chatbox"></div>
    <input type="text" id="userInput" placeholder="Ask me something">
    <button id="sendBtn" onclick="sendMessage()">Send</button>

    <script>
        function sendMessage() {
            let input = document.getElementById("userInput").value;
            let chatbox = document.getElementById("chatbox");

            let userMessage = `<p><strong>You:</strong> ${input}</p>`;
            chatbox.innerHTML += userMessage;

            fetch(`/ask?query=${encodeURIComponent(input)}`)
                .then(response => response.json())
                .then(data => {
                    let botMessage = `<p><strong>Bot:</strong> ${data.message}</p>`;
                    if (data.link) {
                        botMessage += `<p>Read more: <a href='${data.link}' target='_blank'>Click here</a></p>`;
                    }
                    chatbox.innerHTML += botMessage;
                    chatbox.scrollTop = chatbox.scrollHeight;
                });

            document.getElementById("userInput").value = "";
        }
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True)