from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyDdwVlAq2eR5DSeGSOc7Xp2fsVEGsEcSM4"  # ← REPLACE WITH YOUR KEY
genai.configure(api_key=GOOGLE_API_KEY)

# Use the updated model name
model = genai.GenerativeModel('gemini-1.0-pro')  # ← Changed model name

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    
    try:
        response = model.generate_content(message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"})

# Keep the rest of the code (HTML/JS/CSS) from previous answer