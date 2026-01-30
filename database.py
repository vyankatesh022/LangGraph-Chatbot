import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

db_path='chatbot.db'

def get_connection():
    conn=sqlite3.connect(db_path,check_same_thread=False)
    return conn

def init_table():
    conn=get_connection()
    conn.execute('''
            create table if not exists chat_titles(
            thread_id text primary key, title text
             )
    ''')

def get_checkpointer():
    conn=get_connection()
    return SqliteSaver(conn=conn)

def save_title(thread_id, title):
    conn=get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO chat_titles VALUES (?, ?)",
        (thread_id, title)
    )
    conn.commit()

def load_chat_titles():
    conn=get_connection()
    cur = conn.execute("SELECT thread_id, title FROM chat_titles")
    return {row[0]: row[1] for row in cur.fetchall()}