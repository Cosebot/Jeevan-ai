from flask import Flask, Response
import os

app = Flask(__name__)

@app.route('/')
def index():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mega Sanji AI</title>
    <script src="https://js.puter.com/v2/"></script>
    <style>
        *{box-sizing:border-box;margin:0;padding:0;}
        body{font-family:'Poppins',sans-serif;background:#000;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;overflow:hidden;}
        #loadingScreen{display:flex;flex-direction:column;align-items:center;justify-content:center;}
        .loader{border:6px solid #333;border-top:6px solid #0066ff;border-radius:50%;width:80px;height:80px;animation:spin 1s linear infinite;margin-bottom:20px;}
        @keyframes spin{0%{transform:rotate(0deg);}100%{transform:rotate(360deg);}}
        #status{font-size:16px;text-align:center;margin-top:10px;}
        #aiContainer{display:none;flex-direction:column;height:100vh;width:100%;}
        .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    width: 100%;
    max-width: 420px;
    padding: 15px;
    padding-bottom: 90px; /* add this */
    background: linear-gradient(180deg,#1b1b1b,#000);
    border-radius: 12px;
    overflow-y: auto;
    scroll-behavior: smooth;
    margin-bottom: 70px;
}
        .message{background:#222;padding:12px 16px;border-radius:14px;margin:8px 0;max-width:80%;word-wrap:break-word;line-height:1.4;animation:fadeIn 0.3s ease;}
        .user{align-self:flex-end;background:#0066ff;}
        .ai{align-self:flex-start;background:#333;}
        img.generated{width:100%;border-radius:12px;margin-top:10px;box-shadow:0 0 10px rgba(0,0,0,0.4);animation:fadeIn 0.3s ease;}
        @keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
        .input-bar{display:flex;align-items:center;justify-content:space-between;width:100%;padding:10px;background:#111;position:fixed;bottom:0;left:0;z-index:999;border-top:1px solid #333;}
        .input-bar input{flex:1;background:#000;color:#fff;border:none;padding:12px;border-radius:8px;outline:none;font-size:15px;margin-right:8px;}
        .input-bar button{flex-shrink:0;margin-left:4px;background:#0066ff;color:white;border:none;border-radius:8px;padding:10px 12px;cursor:pointer;font-weight:bold;transition:background 0.2s;}
        .input-bar button:hover{background:#0052cc;}
        .btn-small{font-size:13px;padding:10px 10px;background:#00c2ff;}
        .btn-small:hover{background:#009fd1;}
        button,input,a{-webkit-tap-highlight-color:transparent;touch-action:manipulation;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;}
    </style>
</head>
<body>

    <!-- Loader -->
    <div id="loadingScreen">
        <div class="loader"></div>
        <div id="status">Initializing...</div>
    </div>

    <!-- AI Container -->
    <div id="aiContainer">
        <div class="chat-container" id="chatContainer">
            <div class="message ai">
                Welcome to Mega Sanji AI! 💬 Ask me anything or generate images 🖼️
            </div>
        </div>

        <div class="input-bar">
            <input type="text" id="userInput" placeholder="Type your message or image prompt..." />
            <button id="sendBtn">💬</button>
            <button id="imgBtn" class="btn-small">🖼️</button>
        </div>
    </div>

<script>
const statuses = [
    "Firing up the brain....",
    "Heart starting to beat...",
    "Eyes opening....",
    "Loading....",
    "Making the UI Beautiful for you....",
    "Done!"
];
const statusEl = document.getElementById("status");
const loadingScreen = document.getElementById("loadingScreen");
const aiContainer = document.getElementById("aiContainer");

function scrollToBottom(chat){ chat.scrollTop = chat.scrollHeight; }

function appendMessage(chat, text, sender){
    const div = document.createElement("div");
    div.className = "message " + sender;
    div.textContent = text;
    chat.appendChild(div);
    scrollToBottom(chat);
    return div;
}

function waitForPuter(){
    return new Promise(resolve=>{
        if(window.puter && window.puter.ai) resolve();
        else window.addEventListener('puter:loaded', resolve);
    });
}

async function startMegaSanjiAI(){
    const chat = document.getElementById("chatContainer");
    const input = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const imgBtn = document.getElementById("imgBtn");

    sendBtn.addEventListener("click", sendMessage);
    imgBtn.addEventListener("click", generateImage);
    input.addEventListener("keydown", (e)=>{ if(e.key==="Enter") sendMessage(); });

    async function sendMessage(){
        const text = input.value.trim();
        if(!text) return;
        appendMessage(chat, text, "user");
        input.value = "";
        const aiMsg = appendMessage(chat, "Thinking...", "ai");

        try{
            await waitForPuter();
            const start = Date.now();
            const response = await puter.ai.chat(text, { model: "gpt-5" });
            const elapsed = Date.now() - start;
            
            // If response is super fast, add a tiny delay to feel natural (max 2s)
            if(elapsed < 1000) await new Promise(r=>setTimeout(r, 1000));

            aiMsg.textContent = response;
            scrollToBottom(chat);
        } catch(err){
            aiMsg.textContent = "⚠️ Error: "+(err.message||"Unknown error");
        }
    }

   async function generateImage() {
    const text = input.value.trim();
    if (!text) return;

    // Show user's prompt in chat
    appendMessage(chat, text, "user");
    input.value = "";

    // Temporary "thinking" message
    const aiMsg = appendMessage(chat, "🎨 Generating image...", "ai");

    try {
        // Wait until puter is loaded
        await waitForPuter();

        // Generate image (usually returns a URL)
        const imgUrl = await puter.ai.txt2img(text, { model: "dall-e-3" });

        // Replace "thinking" text with actual image
        aiMsg.textContent = "Here's your image:";
        const img = document.createElement("img");
        img.src = imgUrl;           // set the generated image URL
        img.classList.add("generated");

        // Append image inside chat
        chat.appendChild(img);
        scrollToBottom(chat);

    } catch (err) {
        aiMsg.textContent = "⚠️ Error generating image: " + (err.message || "Unknown error");
        console.error("Generate Image Error:", err);
    }
}
}

// Loader (1 min)
async function dynamicLoading(){
    const totalTime = 60000;
    const interval = totalTime / statuses.length;
    for(let i=0;i<statuses.length;i++){
        statusEl.textContent = statuses[i];
        await new Promise(r=>setTimeout(r, interval));
    }
    await waitForPuter();
    loadingScreen.style.display="none";
    aiContainer.style.display="flex";
    startMegaSanjiAI();
}

dynamicLoading();
</script>
</body>
</html>
"""
    return Response(html_content, mimetype='text/html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port, threaded=True)