# mega_sanji_ai_with_tts.py

from flask import Flask, Response, request, send_file, jsonify
import os
import tempfile
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

app = Flask(__name__)

# -----------------------
# Project-Alpha TTS Engine
# -----------------------
class ChefsKissTTS:
    def __init__(self, sr=22050):
        self.sr = sr
        self.base_freq = 100         # deep base pitch
        self.harmonics = [1, 2, 3]   # harmonics for richness

    def text_to_phonemes(self, text):
        phonemes = []
        for c in text:
            if c.isalpha():
                phonemes.append(ord(c) % 40 + 60)
            elif c in ",;:":
                phonemes.append(30)  # slight pause
            elif c in ".!?":
                phonemes.append(20)  # longer pause
        if not phonemes:
            phonemes = [100]
        return phonemes

    def apply_lowpass_filter(self, audio, cutoff=700):
        nyq = 0.5 * self.sr
        normal_cutoff = cutoff / nyq
        b, a = butter(2, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, audio)

    def phonemes_to_wave(self, phonemes):
        audio = np.array([])
        for f in phonemes:
            duration = 0.25
            if f <= 30: duration = 0.35
            elif f <= 20: duration = 0.5

            t = np.linspace(0, duration, int(self.sr*duration))
            wave = np.zeros_like(t)

            for h in self.harmonics:
                freq = (self.base_freq + f) * h
                vibrato = 3 * np.sin(2*np.pi*5*t)
                wave += (0.25 / h) * np.sin(2*np.pi*(freq + vibrato)*t)

            envelope = np.linspace(0.1,1,len(t)) * np.linspace(1,0.9,len(t))
            wave *= envelope
            wave = self.apply_lowpass_filter(wave, cutoff=700)
            audio = np.concatenate([audio, wave])
        return audio

    def generate_temp_audio(self, text):
        phonemes = self.text_to_phonemes(text)
        audio = self.phonemes_to_wave(phonemes)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp_file.close()
        sf.write(tmp_file.name, audio, self.sr)
        return tmp_file.name

    def speak_and_cleanup(self, text):
        file_path = self.generate_temp_audio(text)
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
        os.remove(file_path)
        return audio_bytes

tts_engine = ChefsKissTTS()

# -----------------------
# Flask Routes
# -----------------------

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
/* ---------- FULL ORIGINAL CSS ---------- */
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
    if(sender === "ai") speakText(text);
    return div;
}

// TTS call
async function speakText(text){
    try{
        const res = await fetch("/tts?text="+encodeURIComponent(text));
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
    }catch(err){
        console.warn("TTS Error:", err);
    }
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
            speakText(response);
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

# -----------------------
# TTS Endpoint
# -----------------------
@app.route('/tts')
def tts_route():
    text = request.args.get("text","Hello")
    audio_bytes = tts_engine.speak_and_cleanup(text)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp_file.write(audio_bytes)
    tmp_file.close()
    return send_file(tmp_file.name, mimetype="audio/wav", as_attachment=False)

# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port, threaded=True)