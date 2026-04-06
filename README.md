# LangGraph-Chatbot

A Streamlit chat app with model selection, MySQL-backed chat history, and PDF RAG for document analysis.

## Features

- Gemini and OpenAI model selection
- chat history stored in MySQL
- automatic chat title generation
- assistant modes:
  - `general`
  - `all_in_one`
  - `pdf_analysis`
- PDF upload and retrieval for the current thread
- streaming assistant responses in the UI

## Project Structure

```text
.
├── app.py
├── backend.py
├── database.py
├── rag.py
└── README.md
```

## Files

- `app.py`: Streamlit UI, sidebar controls, PDF upload, and chat display
- `backend.py`: model setup, title generation, text chat, PDF chat, and response streaming
- `database.py`: MySQL connection, table creation, and message/title storage
- `rag.py`: PDF loading, chunking, embeddings, FAISS storage, and retrieval

## Requirements

- Python 3.10+
- MySQL
- Google API key for Gemini and embeddings
- OpenAI API key if you want to use the OpenAI option

## Environment Setup

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=langgraph_chatbot
```

## Install

```bash
pip install streamlit python-dotenv mysql-connector-python langchain-core langchain-openai langchain-google-genai langchain-community langchain-text-splitters faiss-cpu pypdf
```

## Run

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## How It Works

1. A new chat gets a unique `thread_id`.
2. Messages and titles are saved in MySQL.
3. You can choose a model and assistant mode from the sidebar.
4. In `pdf_analysis` mode, upload a PDF for the current thread.
5. The app chunks the PDF, stores embeddings in FAISS, retrieves relevant chunks, and answers using that context.

## PDF RAG Notes

- one PDF context is stored per thread
- uploading a new PDF replaces the old PDF context for that thread
- FAISS indexes are stored in the system temp directory
- retrieval is used only in `pdf_analysis` mode

## Database Tables

The app creates these tables automatically:

- `chat_titles`
- `chat_messages`