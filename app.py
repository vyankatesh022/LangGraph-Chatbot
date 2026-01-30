import streamlit as st
import uuid

from backend import stream_chat, generate_and_save_title, load_existing_chat
from database import init_table, load_chat_titles

def init_state():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "titles" not in st.session_state:
        st.session_state.titles = load_chat_titles()

def side_bar():
    st.sidebar.title('AI Chat')

    if st.sidebar.button('New Chat'):
        st.session_state.messages=[]
        st.session_state.thread_id=str(uuid.uuid4())

    st.sidebar.header('Chat')

    for thread_id in reversed(list(st.session_state.titles.keys())):
        title=st.session_state.titles.get(thread_id, "Untitled Chat")
        if st.sidebar.button(title, key=thread_id):
            st.session_state.thread_id = thread_id
            st.session_state.messages = load_existing_chat(thread_id)

def display_chats():
    for data in st.session_state.messages:
        with st.chat_message(data['role']):
            st.text(data['content'])

if __name__=='__main__':

    st.title("LangGraph Chatbot")

    init_table()
    init_state()
    side_bar()
    display_chats()

    config={'configurable':{'thread_id':st.session_state.thread_id}}

    user_input=st.chat_input('Type Here')

    if user_input:
        # user
        st.session_state.messages.append({'role':'user','content':user_input})
        with st.chat_message('user'):
            st.text(user_input)

        #title
        thread=st.session_state.thread_id
        if thread not in st.session_state.titles:
            title=generate_and_save_title(thread, user_input)
            st.session_state.titles[thread] = title

        # assistance
        with st.chat_message('assistant'):
            def stream():
                for msg, _ in stream_chat(user_input, thread):
                    if msg.content:
                        yield msg.content
            ai_text=st.write_stream(stream)
        st.session_state.messages.append({'role':'assistant','content':ai_text})