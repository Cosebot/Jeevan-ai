import requests
from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)

def search_duckduckgo(query):
    """Fetches first result title, link, and article text from DuckDuckGo."""
    search_url = f"https://lite.duckduckgo.com/lite?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a", class_="result-link")
        
        if results:
            article_title = results[0].text.strip()  
            article_link = results[0]['href']
            
            # Fetch the actual article content
            article_text = fetch_article_text(article_link)[:1000]  # First 1000 characters
            return article_title, article_text, article_link
        
    return "No relevant information found.", "", ""

def fetch_article_text(url):
    """Scrapes the main text of the given article URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        paragraphs = soup.find_all("p")  # Extract paragraphs
        full_text = "\n".join([p.get_text() for p in paragraphs])  # Combine paragraphs
        
        return full_text.strip() if full_text else "No content found."
    except:
        return "Failed to fetch the article."

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/ask', methods=['GET'])
def ask_chatbot():
    """Processes user input and returns first 1000 characters + link."""
    user_input = request.args.get('query', '').strip().lower()
    
    if any(user_input.startswith(word) for word in ["what", "where", "why", "how", "when"]):
        title, search_results, article_link = search_duckduckgo(user_input)
        return jsonify({"title": title, "message": search_results, "link": article_link})
    
    return jsonify({"message": "I only answer questions starting with What/Where/Why/How/When."})

# Frontend UI (HTML, CSS, and JS)
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
                    let botMessage = `<p><strong>Bot:</strong> <b>${data.title}</b><br>${data.message}</p>`;
                    if (data.link) {
                        botMessage += `<p>Read more: <a href='${data.link}' target='_blank'>Full article</a></p>`;
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