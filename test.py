from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Puter AI Chat</title>
  <script src="https://js.puter.com/v2/"></script>
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #0f0f0f;
      color: #fff;
      font-family: 'Poppins', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      height: 100vh;
      width: 100vw;
    }

    .chat-container {
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      width: 100%;
      height: 100%;
      max-width: 420px;
      padding: 15px;
      box-sizing: border-box;
      background: linear-gradient(180deg, #1b1b1b, #000);
      border-radius: 12px;
      overflow-y: auto;
    }

    .message {
      background: #222;
      padding: 12px 16px;
      border-radius: 14px;
      margin: 8px 0;
      max-width: 80%;
      word-wrap: break-word;
      line-height: 1.4;
      animation: fadeIn 0.3s ease;
    }

    .user {
      align-self: flex-end;
      background: #0066ff;
    }

    .ai {
      align-self: flex-start;
      background: #333;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .input-container {
      width: 100%;
      max-width: 420px;
      display: flex;
      background: #111;
      border-top: 1px solid #333;
      padding: 10px;
      box-sizing: border-box;
    }

    input {
      flex: 1;
      background: #000;
      color: #fff;
      border: none;
      padding: 10px;
      border-radius: 8px;
      outline: none;
      font-size: 15px;
    }

    button {
      margin-left: 10px;
      background: #0066ff;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 10px 15px;
      cursor: pointer;
      font-weight: bold;
      transition: background 0.2s;
    }

    button:hover {
      background: #0052cc;
    }
  </style>
</head>
<body>
  <div class="chat-container" id="chatContainer">
    <div class="message ai">Welcome! Ask me anything 💬</div>
  </div>

  <div class="input-container">
    <input id="userInput" placeholder="Type your question..." />
    <button onclick="sendMessage()">Send</button>
  </div>

  <script>
    async function sendMessage() {
      const input = document.getElementById("userInput");
      const chat = document.getElementById("chatContainer");
      const text = input.value.trim();
      if (!text) return;

      const userMsg = document.createElement("div");
      userMsg.className = "message user";
      userMsg.textContent = text;
      chat.appendChild(userMsg);
      input.value = "";
      chat.scrollTop = chat.scrollHeight;

      const aiMsg = document.createElement("div");
      aiMsg.className = "message ai";
      aiMsg.textContent = "Typing...";
      chat.appendChild(aiMsg);
      chat.scrollTop = chat.scrollHeight;

      try {
        const response = await puter.ai.chat(text, { model: "gpt-5-nano" });
        aiMsg.textContent = response;
      } catch (err) {
        aiMsg.textContent = "⚠️ Error: " + err.message;
      }

      chat.scrollTop = chat.scrollHeight;
    }
  </script>
</body>
</html>
"""
    return Response(html_content, mimetype='text/html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)