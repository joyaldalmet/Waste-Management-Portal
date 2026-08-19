from flask import Flask, render_template, request, jsonify, session
import requests
import json
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest"

BASE_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(BASE_DIR, "data.json")
DB_FILE = os.path.join(BASE_DIR, "db.sqlite")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_message(session_id, role, message):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (session_id, role, message) VALUES (?, ?, ?)",
        (session_id, role, message)
    )
    conn.commit()
    conn.close()


def get_history(session_id, limit=10):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, message FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return list(reversed(rows))  # oldest first


def load_waste_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(session_id, user_message):
    waste_data = load_waste_data()
    history = get_history(session_id, limit=10)

    system_prompt = (
        "You are a helpful waste management assistant chatbot. You help users "
        "understand different types of waste, how to dispose of them, recycling "
        "details, and give practical recommendations and suggestions. Use ONLY "
        "the reference data below along with the conversation history to answer. "
        "If something is not covered, give general best-practice waste management "
        "advice. Keep answers clear, concise, and practical.\n\n"
        f"REFERENCE DATA:\n{json.dumps(waste_data, indent=2)}\n"
    )

    conversation = ""
    for role, message in history:
        speaker = "User" if role == "user" else "Assistant"
        conversation += f"{speaker}: {message}\n"

    full_prompt = (
        f"{system_prompt}\n"
        f"CONVERSATION SO FAR:\n{conversation}\n"
        f"User: {user_message}\n"
        f"Assistant:"
    )
    return full_prompt


@app.route("/")
def index():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    waste_data = load_waste_data()
    return render_template("index.html", categories=waste_data["categories"])


@app.route("/chat", methods=["POST"])
def chat():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    session_id = session["session_id"]

    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "Please type a message."})

    try:
        prompt = build_prompt(session_id, user_message)

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            reply = result.get("response", "Sorry, I couldn't generate a response.").strip()
        else:
            reply = "Error: Could not reach the Ollama model. Make sure Ollama is running."

        save_message(session_id, "user", user_message)
        save_message(session_id, "assistant", reply)

    except requests.exceptions.ConnectionError:
        reply = "Could not connect to Ollama. Please make sure Ollama is running (ollama serve) and the model 'llama3.2:latest' is pulled."
    except Exception as e:
        reply = f"An unexpected error occurred: {str(e)}"

    return jsonify({"reply": reply})


@app.route("/history", methods=["GET"])
def history():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        return jsonify({"history": []})

    session_id = session["session_id"]
    rows = get_history(session_id, limit=50)
    return jsonify({"history": [{"role": r, "message": m} for r, m in rows]})


@app.route("/clear", methods=["POST"])
def clear():
    if "session_id" in session:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("DELETE FROM chat_history WHERE session_id = ?", (session["session_id"],))
        conn.commit()
        conn.close()
    return jsonify({"status": "cleared"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)