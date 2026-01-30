# LangGraph-Chatbot

LangGraph-Chatbot is a **Streamlit-based conversational AI application** built using **LangGraph** and **Google Gemini**. It supports **persistent chat memory**, **automatic chat title generation**, and **real-time streaming responses**, all backed by a lightweight **SQLite database**.

---

## ✨ Features

* 🤖 AI-powered chat using **Google Gemini**
* 🔁 Conversation flow managed with **LangGraph**
* 💾 Persistent chat memory using **SQLite**
* 🏷 Automatic chat title generation
* 📂 Sidebar chat history with resume support
* ⚡ Streaming AI responses for better UX

---

## 🗂 Project Structure

```
.
├── app.py          # Streamlit frontend & session management
├── backend.py      # LangGraph workflow and AI logic
├── database.py     # SQLite database helpers
├── chatbot.db      # Auto-generated SQLite database
└── README.md
```

---

## 📄 File Descriptions

### `app.py`

* Handles the Streamlit UI
* Manages session state and chat threads
* Displays chat messages and sidebar history
* Streams AI responses in real time

### `backend.py`

* Defines the LangGraph state machine
* Configures the Gemini model
* Generates and stores chat titles
* Handles message routing and checkpoints

### `database.py`

* Manages SQLite connections
* Initializes database tables
* Saves and loads chat titles
* Provides LangGraph checkpointer support

---

## ⚙️ Requirements

* Python **3.10+**
* Google Gemini API key

### Python Dependencies

```
streamlit
langgraph
langchain-core
langchain-google-genai
python-dotenv
sqlite3
```

---

## 🔐 Environment Setup

Create a `.env` file in the project root directory:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

---

## ▶️ Running the Application

From the project root:

```bash
streamlit run app.py
```

Then open your browser at:

```
http://localhost:8501
```

---

## 🧠 How ChatFlow AI Works

1. Each new conversation is assigned a unique `thread_id`
2. Messages are processed through a LangGraph workflow
3. Chat history is checkpointed into SQLite
4. The first user message generates a short chat title
5. All chats appear in the sidebar and can be resumed anytime

---

## 🧪 Model Configuration

* **Model:** Gemini 2.5 Flash
* **Temperature:** 0
* **Max Tokens:** 50

These settings ensure fast, concise responses.

---

## 📌 Notes

* The database file (`chatbot.db`) is created automatically
* Chat titles are limited to **6 words**
* Supports multiple chat sessions in a single browser

---

## 🚀 Future Enhancements

* User authentication
* Chat export (PDF / TXT)
* Multi-model support
* Improved UI styling
* Searchable chat history