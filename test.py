from flask import Flask, Response

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
* { box-sizing: border-box; }
body { margin:0; padding:0; background:#000; color:#fff;
       font-family:'Poppins', sans-serif; display:flex;
       justify-content:center; align-items:center; height:100vh; overflow:hidden; }

/* Loading Screen */
#loadingScreen { display:flex; flex-direction:column; align-items:center; justify-content:center; }
.loader { border:6px solid #333; border-top:6px solid #0066ff;
         border-radius:50%; width:80px; height:80px; animation:spin 1s linear infinite;
         margin-bottom:20px; }
@keyframes spin { 0%{transform:rotate(0deg);} 100%{transform:rotate(360deg);} }
#status { font-size:16px; text-align:center; margin-top:10px; }

/* AI Container */
#aiContainer { display:none; flex-direction:column; height:100vh; width:100%; }

/* Chat container */
.chat-container {
    flex:1; display:flex; flex-direction:column; justify-content:flex-start;
    width:100%; max-width:420px; padding:15px;
    background: linear-gradient(180deg,#1b1b1b,#000);
    border-radius:12px; overflow-y:auto; scroll-behavior:smooth; margin-bottom:70px;
}

/* Messages */
.message { background:#222; padding:12px 16px; border-radius:14px; margin:8px 0;
          max-width:80%; word-wrap:break-word; line-height:1.4; animation:fadeIn 0.3s ease; }
.user { align-self:flex-end; background:#0066ff; }
.ai { align-self:flex-start; background:#333; }
img.generated { width:100%; border-radius:12px; margin-top:10px; box-shadow:0 0 10px rgba(0,0,0,0.4); animation:fadeIn 0.3s ease; }

@keyframes fadeIn { from {opacity:0; transform:translateY(10px);} to{opacity:1; transform:translateY(0);} }

/* Input bar */
.input-bar { display:flex; align-items:center; justify-content:space-between;
             width:100%; padding:10px; background:#111; position:fixed;
             bottom:0; left:0; z-index:999; border-top:1px solid #333; }
.input-bar input { flex:1; background:#000; color:#fff; border:none;
                   padding:12px; border-radius:8px; outline:none; font-size:15px; margin-right:8px; }
.input-bar button { flex-shrink:0; margin-left:4px; background:#0066ff; color:white;
                    border:none; border-radius:8px; padding:10px 12px; cursor:pointer;
                    font-weight:bold; transition:background 0.2s; }
.input-bar button:hover { background:#0052cc; }
.btn-small { font-size:13px; padding:10px 10px; background:#00c2ff; }
.btn-small:hover { background:#009fd1; }

/* Mobile tap fix */
button, input, a { -webkit-tap-highlight-color:transparent; touch-action:manipulation;
                    -webkit-user-select:none; user-select:none; -webkit-touch-callout:none; }
</style>
</head>
<body>

<!-- Loading Screen -->
<div id="loadingScreen">
    <div class="loader"></div>
    <div id="status">Initializing...</div>
</div>

<!-- AI Container -->
<div id="aiContainer">
    <div class="chat-container" id="chatContainer">
        <div class="message ai">Welcome to Mega Sanji AI! 💬 Ask me anything or generate images 🖼️</div>
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
    "Done..."
];

const statusEl = document.getElementById("status");
const loadingScreen = document.getElementById("loadingScreen");
const aiContainer = document.getElementById("aiContainer");
let index=0;

function nextStatus(){
    if(index < statuses.length){
        statusEl.textContent = statuses[index];
        index++;
        setTimeout(nextStatus,1200);
    } else {
        loadingScreen.style.display="none";
        aiContainer.style.display="flex";
        startMegaSanjiAI();
    }
}

nextStatus();

// Safe Puter wrapper
async function safePuterChat(prompt, params){
    await new Promise(resolve=>{
        if(window.puter && window.puter.ai) resolve();
        else window.addEventListener('puter:loaded', resolve);
    });
    try { return await puter.ai.chat(prompt, params); }
    catch(e){ console.error("Puter chat error:",e); throw e; }
}

// Mega Sanji AI Init
async function startMegaSanjiAI(){
    const chat=document.getElementById("chatContainer");
    const input=document.getElementById("userInput");
    const sendBtn=document.getElementById("sendBtn");
    const imgBtn=document.getElementById("imgBtn");

    sendBtn.addEventListener("pointerup",sendMessage);
    imgBtn.addEventListener("pointerup",generateImage);
    input.addEventListener("keydown",(e)=>{ if(e.key==="Enter") sendMessage(); });

    function scrollToBottom(){ setTimeout(()=>{ chat.scrollTop=chat.scrollHeight; },50); }

    function appendMessage(text,sender){
        const div=document.createElement("div");
        div.className="message "+sender;
        div.textContent=text;
        chat.appendChild(div);
        scrollToBottom();
        return div;
    }

    async function sendMessage(){
        const text=input.value.trim();
        if(!text) return;
        appendMessage(text,"user");
        input.value="";
        const aiMsg=appendMessage("Typing...","ai");

        try{
            const response = await safePuterChat(text,{ model:"gpt-5", stream:true, temperature:0.5, max_tokens:500 });
            aiMsg.textContent="";
            for await(const part of response){
                aiMsg.textContent += part?.text||"";
                scrollToBottom();
            }
        } catch(err){
            aiMsg.textContent = "⚠️ Error: " + (err.message || "Unknown error");
        }
    }

    async function generateImage(){
        const text=input.value.trim();
        if(!text) return;
        appendMessage(text,"user");
        input.value="";
        const aiMsg=appendMessage("🎨 Generating image...","ai");

        try{
            await new Promise(resolve=>{
                if(window.puter && window.puter.ai) resolve();
                else window.addEventListener('puter:loaded', resolve);
            });
            const imageElement = await puter.ai.txt2img(text, { model: "dall-e-3" });
            aiMsg.textContent="Here's your image:";
            imageElement.classList.add("generated");
            chat.appendChild(imageElement);
            scrollToBottom();
        } catch(err){
            aiMsg.textContent = "⚠️ Error generating image: " + (err.message || "Unknown error");
        }
    }
}
</script>

</body>
</html>
"""
    return Response(html_content, mimetype='text/html')

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)