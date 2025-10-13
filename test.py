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
  <title>Puter AI Chat + Image</title>
  <script src="https://js.puter.com/v2/"></script>
  <style>
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      padding: 0;
      background: #0f0f0f;
      color: #fff;
      font-family: 'Poppins', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
    }

    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      width: 100%;
      max-width: 420px;
      padding: 15px;
      background: linear-gradient(180deg, #1b1b1b, #000);
      border-radius: 12px;
      overflow-y: auto;
      scroll-behavior: smooth;
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

    img.generated {
      width: 100%;
      border-radius: 12px;
      margin-top: 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.4);
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .input-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      max-width: 420px;
      padding: 10px;
      background: #111;
      border-top: 1px solid #333;
      position: sticky;
      bottom: 0;
    }

    .input-bar input {
      flex: 1;
      background: #000;
      color: #fff;
      border: none;
      padding: 12px;
      border-radius: 8px;
      outline: none;
      font-size: 15px;
    }

    .input-bar button {
      margin-left: 8px;
      background: #0066ff;
      color: white;
      border: none;
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      font-weight: bold;
      transition: background 0.2s;
      flex-shrink: 0;
    }

    .input-bar button:hover {
      background: #0052cc;
    }

    .btn-small {
      font-size: 13px;
      padding: 10px 10px;
      background: #00c2ff;
    }

    .btn-small:hover {
      background: #009fd1;
    }
  </style>
</head>
<body>
  <div class="chat-container" id="chatContainer">
    <div class="message ai">Welcome! Ask me anything 💬 or generate an image 🖼️</div>
  </div>

  <div class="input-bar">
    <input id="userInput" placeholder="Type your message or image prompt..." />
    <button onclick="sendMessage()">💬</button>
    <button class="btn-small" onclick="generateImage()">🖼️</button>
  </div>

  <script>
    const chat = document.getElementById("chatContainer");

    function safeScrollToBottom() {
      const threshold = 50;
      const distanceFromBottom = chat.scrollHeight - chat.scrollTop - chat.clientHeight;
      if (distanceFromBottom < threshold) {
        chat.scrollTop = chat.scrollHeight;
      }
    }

    async function sendMessage() {
      const input = document.getElementById("userInput");
      const text = input.value.trim();
      if (!text) return;

      const userMsg = document.createElement("div");
      userMsg.className = "message user";
      userMsg.textContent = text;
      chat.appendChild(userMsg);
      input.value = "";
      safeScrollToBottom();

      const aiMsg = document.createElement("div");
      aiMsg.className = "message ai";
      aiMsg.textContent = "Typing...";
      chat.appendChild(aiMsg);
      safeScrollToBottom();

      try {
        const response = await puter.ai.chat(text, { model: "gpt-5-nano" });
        aiMsg.textContent = response;
      } catch (err) {
        aiMsg.textContent = "⚠️ Error: " + err.message;
      }

      safeScrollToBottom();
    }

    async function generateImage() {
      const input = document.getElementById("userInput");
      const text = input.value.trim();
      if (!text) return;

      const userMsg = document.createElement("div");
      userMsg.className = "message user";
      userMsg.textContent = text;
      chat.appendChild(userMsg);
      input.value = "";
      safeScrollToBottom();

      const aiMsg = document.createElement("div");
      aiMsg.className = "message ai";
      aiMsg.textContent = "🎨 Generating image...";
      chat.appendChild(aiMsg);
      safeScrollToBottom();

      try {
        const imageElement = await puter.ai.txt2img(text, { model: "gpt-image-1" });
        aiMsg.textContent = "Here's your image:";
        imageElement.classList.add("generated");
        chat.appendChild(imageElement);
      } catch (err) {
        aiMsg.textContent = "⚠️ Error generating image: " + err.message;
      }

      safeScrollToBottom();
    }
  </script>
</body>
</html>
"""
    return Response(html_content, mimetype='text/html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)