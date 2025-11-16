from flask import Flask, request, jsonify
from functools import wraps
from agent import HRAssistAgent
import os
import jwt
import datetime
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "your-secret-key")

from database import get_db_path

def log_event(user_id, action, details):
    timestamp = datetime.datetime.now().isoformat()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO audit_log (timestamp, user_id, action, details) VALUES (?, ?, ?, ?)", (timestamp, user_id, action, details))
    conn.commit()
    conn.close()

# Initialize the HR-Assist agent
try:
    agent = HRAssistAgent()
except Exception as e:
    print(f"Error initializing HR-Assist: {e}")
    agent = None

# Mock user database
users = {
    "testuser": {
        "password": "password",
        "user_id": "EMP-123",
        "user_name": "John Doe"
    }
}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users.get(data['username'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route("/")
def index():
    return "HR-Assist agent is running."

@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Could not verify'}), 401

    user = users.get(auth.username)
    if user and user['password'] == auth.password:
        token = jwt.encode({
            'username': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Could not verify'}), 401

@app.route("/chat", methods=["POST"])
@token_required
def chat(current_user):
    if not agent:
        return jsonify({"error": "HR-Assist agent not initialized"}), 500

    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    log_event(current_user['user_id'], 'chat', user_message)
    response = agent.chat(
        user_message=user_message,
        authenticated_user_id=current_user['user_id'],
        user_name=current_user['user_name'],
    )

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
