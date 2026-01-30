from langgraph.graph import StateGraph, START,  END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

chat= ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    max_tokens=50)

class chat_state(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

def chat_node(state: chat_state):
    return {'message':[chat.invoke(state['message'])]}

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in check_pointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)

# memory
conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
conn.execute('''
    create table if not exists chat_titles(
             thread_id text primary key, title text
             )
''')


def generate_title(message):
    prompt=(
        f'''create a short chat title (max 6 words).
          summarizing the following message :\n\n
          {message}'''
    )
    return chat.invoke(prompt).content.strip().replace('"', '')

def save_title(thread_id,title):
    conn.execute(
        "INSERT OR REPLACE INTO chat_titles (thread_id, title) VALUES (?, ?)",
        (str(thread_id), title)
    )
    conn.commit()

def load_chat_titles():
    cur = conn.execute("SELECT thread_id, title FROM chat_titles")
    return {row[0]: row[1] for row in cur.fetchall()}

check_pointer = SqliteSaver(conn=conn)

#graph
graph=StateGraph(chat_state)

# node
graph.add_node('node',chat_node)

# edge
graph.add_edge(START,'node')
graph.add_edge('node',END)

chatbot=graph.compile(checkpointer=check_pointer)