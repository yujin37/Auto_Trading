from flask import Flask, request, jsonify
import sqlite3
import bcrypt
from flask_cors import CORS
import os
app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trading.db")

def get_connection():
    print("DB file path:", DB_PATH)
    return sqlite3.connect(DB_PATH)
def hash_password(user_pw: str) -> str:
    hashed_pw: bytes = bcrypt.hashpw(user_pw.encode("UTF-8"), salt=bcrypt.gensalt())
    return hashed_pw.decode("UTF-8")
def verify_password(user_pw: str, hashed_pw: str) -> bool:
    return bcrypt.checkpw(user_pw.encode("UTF-8"), hashed_pw.encode("UTF-8"))

def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False

    stored_hash = row[0]  # str
    return verify_password(password, stored_hash)
    

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if check_login(username, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Login failed"}), 401

if __name__ == '__main__':
    app.run(debug=True)