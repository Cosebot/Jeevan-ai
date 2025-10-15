# mega_sanji_ai_with_tts.py
from flask import Flask, Response, request, send_file, jsonify
import os, tempfile
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter

# ---------------------------
# Project-Alpha TTS Engine
# ---------------------------
class ChefsKissTTS:
    def __init__(self, sr=22050):
        self.sr = sr
        self.base_freq = 100
        self.harmonics = [1,2,3]

    def text_to_phonemes(self, text):
        phonemes = []
        for c in text:
            if c.isalpha():
                phonemes.append(ord(c)%40 + 60)
            elif c in ",;:":
                phonemes.append(30)
            elif c in ".!?":
                phonemes.append(20)
        if not phonemes:
            phonemes = [100]
        return phonemes

    def apply_lowpass_filter(self, audio, cutoff=700):
        nyq = 0.5 * self.sr
        normal_cutoff = cutoff / nyq
        b,a = butter(2, normal_cutoff, btype='low', analog=False)
        return lfilter(b,a,audio)

    def phonemes_to_wave(self, phonemes):
        audio = np.array([])
        for f in phonemes:
            duration = 0.25
            if f <= 30: duration = 0.35
            elif f <= 20: duration = 0.5
            t = np.linspace(0,duration,int(self.sr*duration))
            wave = np.zeros_like(t)
            for h in self.harmonics:
                freq = (self.base_freq + f) * h
                vibrato = 3 * np.sin(2*np.pi*5*t)
                wave += (0.25/h) * np.sin(2*np.pi*(freq+vibrato)*t)
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
        with open(file_path,"rb") as f:
            audio_bytes = f.read()
        os.remove(file_path)
        return audio_bytes

# Instantiate TTS
tts_engine = ChefsKissTTS()

# ---------------------------
# Flask Bot
# ---------------------------
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
/* ... all your existing CSS ... (same as before) ... */
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

async function playAudio(text){
    try{
        const res = await fetch("/tts?text="+encodeURIComponent(text));
        if(res.ok){
            const blob = await res.blob();
            const audio = new Audio(URL.createObjectURL(blob));
            audio.play();
        }
    }catch(err){ console.error("TTS Error:", err); }
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
            playAudio(response); // <-- speak AI response
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


# ---------------------------
# TTS Endpoint
# ---------------------------
@app.route('/tts')
def tts_endpoint():
    text = request.args.get("text","Hello Mega Sanji AI!")
    audio_bytes = tts_engine.speak_and_cleanup(text)
    tmp_file = tempfile.NamedTemporaryFile(delete=False,suffix=".wav")
    tmp_file.close()
    with open(tmp_file.name,"wb") as f:
        f.write(audio_bytes)
    return send_file(tmp_file.name, mimetype="audio/wav", as_attachment=False)

# ---------------------------
# Run Flask
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(debug=True, host="0.0.0.0", port=port, threaded=True)