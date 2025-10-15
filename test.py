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
body{
    font-family:'Poppins',sans-serif;
    background: linear-gradient(135deg, #FF7F50, #FFB347, #6A0DAD);
    color:#fff;
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
    overflow:hidden;
}
#loadingScreen{
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    width:100%;
    height:100vh;
}
#loadingScreen img{
    width:160px;
    height:160px;
    margin-bottom:30px;
    animation: pulse 1s infinite;
}
#status{
    font-size:32px;
    font-weight:bold;
    text-align:center;
    margin-top:20px;
    text-shadow: 0 0 10px rgba(255,255,255,0.8);
}
@keyframes pulse{
    0%,100%{transform:scale(1);}
    50%{transform:scale(1.1);}
}
#aiContainer{
    display:none;
    flex-direction:column;
    height:100vh;
    width:100%;
    background: linear-gradient(135deg, #FF7F50, #FFB347, #6A0DAD);
}
.chat-container{
    flex:1;
    display:flex;
    flex-direction:column;
    justify-content:flex-start;
    width:100%;
    max-width:420px;
    padding:20px;
    padding-bottom:90px;
    background: linear-gradient(180deg,#FF7F50,#FFB347,#6A0DAD);
    border-radius:12px;
    overflow-y:auto;
    scroll-behavior:smooth;
    margin-bottom:70px;
    box-shadow: 0 0 20px rgba(0,0,0,0.4);
}
.message{
    background: rgba(0,0,0,0.4);
    padding:14px 18px;
    border-radius:16px;
    margin:10px 0;
    max-width:80%;
    word-wrap:break-word;
    line-height:1.4;
    animation:fadeIn 0.3s ease;
    color:#fff;
}
.user{align-self:flex-end;background: rgba(0,102,255,0.8);}
.ai{align-self:flex-start;background: rgba(51,51,51,0.8);}
img.generated{
    width:100%;
    border-radius:12px;
    margin-top:10px;
    box-shadow:0 0 10px rgba(0,0,0,0.4);
    animation:fadeIn 0.3s ease;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.input-bar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    width:100%;
    padding:12px;
    background: rgba(0,0,0,0.6);
    position:fixed;
    bottom:0;
    left:0;
    z-index:999;
    border-top:1px solid #333;
    backdrop-filter: blur(6px);
}
.input-bar input{
    flex:1;
    background: rgba(0,0,0,0.7);
    color:#fff;
    border:none;
    padding:14px;
    border-radius:10px;
    outline:none;
    font-size:16px;
    margin-right:8px;
}
.input-bar button{
    flex-shrink:0;
    margin-left:4px;
    background:#0066ff;
    color:white;
    border:none;
    border-radius:10px;
    padding:12px 14px;
    cursor:pointer;
    font-weight:bold;
    transition:background 0.2s;
}
.input-bar button:hover{background:#0052cc;}
.btn-small{font-size:14px;padding:10px 12px;background:#00c2ff;}
.btn-small:hover{background:#009fd1;}
button,input,a{-webkit-tap-highlight-color:transparent;touch-action:manipulation;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;}
</style>
</head>
<body>

<!-- Loader -->
<div id="loadingScreen">
    <img src="https://media1.giphy.com/media/v1.Y2lkPTZjMDliOTUyeWQyaHFqYXE1N3Q5cHozZzcxYWcxbTRhbnV5MDMxbmJncGh5YzNmeiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/2WGxCWxmBOKF6vfgKK/giphy.gif" alt="Loading...">
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
const statuses = ["Firing up the brain....","Heart starting to beat...","Eyes opening....","Loading....","Making the UI Beautiful for you....","Done!"];
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

function waitForPuter(timeout=10000){
    return new Promise((resolve,reject)=>{
        if(window.puter && window.puter.ai) resolve();
        else{
            const timer = setTimeout(()=>reject(new Error("Puter failed to load")),timeout);
            window.addEventListener('puter:loaded',()=>{clearTimeout(timer);resolve();});
        }
    });
}

async function startMegaSanjiAI(){
    const chat=document.getElementById("chatContainer");
    const input=document.getElementById("userInput");
    const sendBtn=document.getElementById("sendBtn");
    const imgBtn=document.getElementById("imgBtn");

    sendBtn.addEventListener("click",sendMessage);
    imgBtn.addEventListener("click",generateImage);
    input.addEventListener("keydown",(e)=>{if(e.key==="Enter")sendMessage();});

    async function sendMessage(){
        const text=input.value.trim();
        if(!text) return;
        appendMessage(chat,text,"user");
        input.value="";
        const aiMsg=appendMessage(chat,"Thinking...","ai");
        try{
            await waitForPuter();
            const start=Date.now();
            const response=await puter.ai.chat(text,{model:"gpt-5"});
            const elapsed=Date.now()-start;
            if(elapsed<1000) await new Promise(r=>setTimeout(r,1000));
            aiMsg.textContent=response;
            scrollToBottom(chat);
        }catch(err){ aiMsg.textContent="⚠️ Error:"+ (err.message||"Unknown error"); }
    }

    async function generateImage(){
        const text=input.value.trim();
        if(!text) return;
        appendMessage(chat,text,"user");
        input.value="";
        const aiMsg=appendMessage(chat,"","ai");

        async function typeStatus(msg,delay=50){
            aiMsg.textContent="";
            for(let i=0;i<msg.length;i++){
                aiMsg.textContent+=msg[i];
                await new Promise(r=>setTimeout(r,delay));
                scrollToBottom(chat);
            }
        }

        try{
            await waitForPuter();
            if(!puter.ai.txt2img){await typeStatus("⚠️ Image generation not supported."); return;}

            await typeStatus("🎨 Painting your image... ✍️");
            const lowResUrl=await puter.ai.txt2img(text,{model:"gpt-image-1",size:"256x256"});
            const img=document.createElement("img");
            img.src=lowResUrl;
            img.classList.add("generated");
            img.style.filter="blur(8px)";
            img.style.transition="filter 1s ease, transform 1s ease, opacity 0.8s ease";
            img.style.opacity="0";
            chat.appendChild(img);
            scrollToBottom(chat);
            setTimeout(()=>{img.style.opacity="1";},100);

            await typeStatus("🔍 Refining to high-res...");
            const highResUrl=await puter.ai.txt2img(text,{model:"gpt-image-1",size:"1080p"});
            img.src=highResUrl;
            img.style.filter="blur(0px)";
            img.style.transform="scale(1.05)";
            setTimeout(()=>{img.style.transform="scale(1)";},300);

            await typeStatus("✅ Your masterpiece is ready!");

        }catch(err){
            aiMsg.textContent="⚠️ Error generating image:\\n"+JSON.stringify(err,null,2);
            console.error("Generate Image Error:",err);
        }
    }
}

async function dynamicLoading(){
    const totalTime=60000;
    const interval=totalTime/statuses.length;
    for(let i=0;i<statuses.length;i++){statusEl.textContent = statuses[i];
        await new Promise(r => setTimeout(r, interval));
    }
    try {
        await waitForPuter();
    } catch(err) {
        console.warn(err.message);
        statusEl.textContent = "⚠️ Puter failed to load. Continuing...";
        await new Promise(r=>setTimeout(r,1500));
    }
    loadingScreen.style.display = "none";
    aiContainer.style.display = "flex";
    startMegaSanjiAI();
}

document.addEventListener("DOMContentLoaded", dynamicLoading);
</script>
</body>
</html>
"""
    return Response(html_content, mimetype='text/html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port, threaded=True)