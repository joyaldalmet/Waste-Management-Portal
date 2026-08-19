# ♻️ Waste Management Chatbot

A Flask-based waste management assistant that uses **Ollama's LLaMA 3.2** model to answer user queries on waste types, disposal, and recycling, with **SQLite-backed memory** to retain conversation context across messages. The frontend, styled entirely with **Bootstrap**, displays categorized waste information on the main page and offers an interactive chatbot via a floating icon for personalized recommendations.

---

## 📁 Project Structure

```
session3/
├── app.py                 # Flask application (routes, Ollama integration, DB logic)
├── data.json               # Waste category reference data (description, recycling, tips)
├── db.sqlite                # SQLite database for chat memory (auto-created on first run)
└── templates/
    └── index.html            # Bootstrap-based frontend + chatbot UI
```

---

## ✨ Features

- 🗂️ **Waste category reference page** — types, descriptions, recycling details, and recommendations, rendered from `data.json`
- 💬 **Floating chatbot icon** (bottom-right) that opens a Bootstrap Offcanvas chat panel
- 🧠 **Persistent memory** — conversation history is stored per browser session in `db.sqlite`, so the bot retains context across messages and page reloads
- 🤖 **LLaMA 3.2 powered** via a local Ollama server — no external API calls
- 🎨 **Pure Bootstrap styling** — no custom CSS files; only inline `<script>` used for `fetch()` calls to the Flask backend
- 🧹 **Clear conversation** option to reset chat memory

---

## ⚙️ Requirements

- Python 3.8+
- [Ollama](https://ollama.com) installed and running locally
- `llama3.2:latest` model pulled in Ollama

---

## 🚀 Setup & Installation

1. **Pull and start the Ollama model**
   ```bash
   ollama pull llama3.2:latest
   ollama serve
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask requests
   ```

3. **Run the Flask app**
   ```bash
   cd session3
   python app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000/
   ```

> `db.sqlite` is created automatically on first run — no manual setup needed.

---

## 🧠 How Memory Works

- Each browser session is assigned a unique `session_id` via Flask's cookie-based session.
- Every user message and bot reply is saved to `db.sqlite`, tagged with that `session_id`.
- On each new message, the last 10 exchanges are retrieved from the database and included in the prompt sent to Ollama, giving the model conversational context.
- Refreshing the page reloads history via the `/history` endpoint, so the conversation persists.
- The **"Clear Conversation"** button wipes that session's rows from the database.

---

## 🔌 API Endpoints

| Route      | Method | Description                                      |
|------------|--------|---------------------------------------------------|
| `/`        | GET    | Renders the main page with waste categories        |
| `/chat`    | POST   | Sends a user message, returns the bot's reply       |
| `/history` | GET    | Returns the current session's chat history          |
| `/clear`   | POST   | Clears the current session's chat history           |

---

## 📝 Notes

- `data.json` contains the reference dataset the chatbot is grounded on for waste type, description, recycling details, and recommendations — edit it to expand or customize the knowledge base.
- Update `app.secret_key` in `app.py` before any real deployment.
- Bootstrap is loaded via CDN (`<link>`/`<script>` tags); the only custom code is the inline JavaScript needed for `fetch()` calls to the backend and dynamic chat rendering.
- Make sure `ollama serve` is running in the background before starting the Flask app, or chatbot replies will fail with a connection error.

---

## 🛠️ Built With

- [Flask](https://flask.palletsprojects.com/) — Python web framework
- [Ollama](https://ollama.com) + LLaMA 3.2 — local LLM inference
- [Bootstrap 5](https://getbootstrap.com/) — frontend styling & components
- SQLite — lightweight persistent chat memory
