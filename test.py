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
<script src="https://js.puter.com/v2/" onload="initMegaSanjiAI()"></script>
<style>
* { box-sizing: border-box; }
body {
    margin:0; padding:0;
    background:#0f0f0f; color:#fff;
    font-family:'Poppins', sans-serif;
    display:flex; flex-direction:column;
    height:100vh; width:100vw; overflow:hidden;
}
/* Chat container */
.chat-container {
    flex:1; display:flex; flex-direction:column;
    justify-content:flex-start; width:100%;
    max-width:420px; padding:15px;
    background: linear-gradient(180deg,#1b1b1b,#000);
    border-radius:12px; overflow-y:auto;
    scroll-behavior:smooth; margin-bottom:70px;
}
/* Messages */
.message {
    background:#222; padding:12px 16px;
    border-radius:14px; margin:8px 0;
    max-width:80%; word-wrap:break-word;
    line-height:1.4; animation:fadeIn 0.3s ease;
}
.user { align-self:flex-end; background:#0066ff; }
.ai { align-self:flex-start; background:#333; }
img.generated {
    width:100%; border-radius:12px;
    margin-top:10px; box-shadow:0 0 10px rgba(0,0,0,0.4);
    animation:fadeIn 0.3s ease;
}
@keyframes fadeIn { from {opacity:0; transform:translateY(10px);} to{opacity:1; transform:translateY(0);} }

/* Input bar */
.input-bar {
    display:flex; align-items:center; justify-content:space-between;
    width:100%; padding:10px; background:#111;
    position:fixed; bottom:0; left:0; z-index:999;
    border-top:1px solid #333;
}
.input-bar input {
    flex:1; background:#000; color:#fff;
    border:none; padding:12px; border-radius:8px;
    outline:none; font-size:15px; margin-right:8px;
}
.input-bar button {
    flex-shrink:0; margin-left:4px; background:#0066ff;
    color:white; border:none; border-radius:8px;
    padding:10px 12px; cursor:pointer; font-weight:bold;
    transition:background 0.2s;
}
/* Hover effect */
.input-bar button:hover { background:#0052cc; }
.btn-small { font-size:13px; padding:10px 10px; background:#00c2ff; }
.btn-small:hover { background:#009fd1; }

/* MOBILE TAP FIX */
button, input, a {
    -webkit-tap-highlight-color: transparent; /* removes green flash */
    touch-action: manipulation;
    -webkit-user-select:none;
    user-select:none;
    -webkit-touch-callout:none;
}
</style>
</head>
<body>

<div class="chat-container" id="chatContainer">
    <div class="message ai">Welcome to Mega Sanji AI! 💬 Ask me anything or generate images 🖼️</div>
</div>

<div class="input-bar">
    <input type="text" id="userInput" placeholder="Type your message or image prompt..." />
    <button id="sendBtn">💬</button>
    <button id="imgBtn" class="btn-small">🖼️</button>
</div>

<script>
function initMegaSanjiAI(){
    requestAnimationFrame(()=>{
        const chat=document.getElementById("chatContainer");
        const input=document.getElementById("userInput");
        const sendBtn=document.getElementById("sendBtn");
        const imgBtn=document.getElementById("imgBtn");

        if(!sendBtn||!imgBtn||!input||!chat){
            console.error("DOM elements missing!");
            return;
        }

        // Event listeners
        sendBtn.addEventListener("click", sendMessage);
        imgBtn.addEventListener("click", generateImage);
        input.addEventListener("keydown",(e)=>{ if(e.key==="Enter") sendMessage(); });

        function appendMessage(text,sender){
            const div=document.createElement("div");
            div.className="message "+sender;
            div.textContent=text;
            chat.appendChild(div);
            scrollToBottom();
            return div;
        }

        function scrollToBottom(){ setTimeout(()=>{ chat.scrollTop=chat.scrollHeight; },50); }

        // Streaming GPT-5
        async function sendMessage(){
            const text=input.value.trim();
            if(!text) return;
            appendMessage(text,"user");
            input.value="";
            const aiMsg=appendMessage("Typing...","ai");

            try{
                const response=await puter.ai.chat(text,{
                    model:"gpt-5",
                    stream:true,
                    temperature:0.5,
                    max_tokens:500
                });
                aiMsg.textContent="";
                for await(const part of response){
                    aiMsg.textContent+=part?.text||"";
                    scrollToBottom();
                }
            }catch(err){
                aiMsg.textContent="⚠️ Error: "+err.message;
                scrollToBottom();
            }
        }

        // DALL·E 3
        async function generateImage(){
            const text=input.value.trim();
            if(!text) return;
            appendMessage(text,"user");
            input.value="";
            const aiMsg=appendMessage("🎨 Generating image...","ai");

            try{
                const imageElement=await puter.ai.txt2img(text,{model:"dall-e-3"});
                aiMsg.textContent="Here's your image:";
                imageElement.classList.add("generated");
                chat.appendChild(imageElement);
                scrollToBottom();
            }catch(err){
                aiMsg.textContent="⚠️ Error generating image: "+err.message;
                scrollToBottom();
            }
        }

        // Optional tool/function example
        const tools=[{
            type:"function",
            function:{
                name:"calculate",
                description:"Perform basic math operations",
                parameters:{
                    type:"object",
                    properties:{
                        operation:{type:"string",enum:["add","subtract","multiply","divide"]},
                        a:{type:"number"},
                        b:{type:"number"}
                    },
                    required:["operation","a","b"]
                }
            }
        }];

        puter.ai.chat("What is 15 multiplied by 7?",{tools})
        .then(response=>{
            if(response.message.tool_calls){
                const call=response.message.tool_calls[0];
                const args=JSON.parse(call.function.arguments);
                let result;
                if(args.operation==="multiply"){ result=args.a*args.b; }
                puter.print(`AI requested: ${args.a} × ${args.b} = ${result}`);
            }
        });
    });
}
</script>

</body>
</html>
"""
    return Response(html_content, mimetype='text/html')

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)