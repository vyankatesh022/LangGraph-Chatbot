import streamlit as st
import uuid
import tempfile

from backend import stream_chat, generate_and_save_title, Model_List, assistant_mode
from database import init_table, load_chat_titles, load_thread_messages
from rag import add_docs, delete_store, load_and_split_pdf

def init_state():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id=str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    if "titles" not in st.session_state:
        st.session_state.titles=load_chat_titles()

    if "model" not in st.session_state:
        st.session_state.model=next(iter(Model_List))

    if 'assistant_mode' not in st.session_state:
        st.session_state.assistant_mode=next(iter(assistant_mode))
    
    if 'pdf_name' not in st.session_state:
        st.session_state.pdf_name={}

def handle_dataset():
    thread_id=st.session_state.thread_id
    name=st.session_state.pdf_name
    file=st.sidebar.file_uploader('Upload PDF', type='pdf', key=f'pdf_{thread_id}')

    if not file:
        if thread_id in name:
            st.sidebar.caption(f'Activate PDF: {name[thread_id]}')
        return
    
    marker=(thread_id, file.name, file.size)
    if st.session_state.get('last_uploaded_pdf')==marker:
        st.sidebar.caption(f'Active PDF : {file.name}')
        return

    import os, tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(file.getvalue())
        path=tmp.name

    try:
        delete_store(thread_id)
        add_docs(thread_id, load_and_split_pdf(path))
        name[thread_id]=file.name
        st.session_state.last_uploaded_pdf=marker
        st.sidebar.success(f'Index {file.name}')
    finally:
        if os.path.exists(path):
            os.remove(path)

def dataset_clear():
    thread_id=st.session_state.thread_id
    pdf_name=st.session_state.pdf_name.get(thread_id)

    if pdf_name:
        st.sidebar.caption(f"Active PDF: {pdf_name}")

    if st.sidebar.button('Clear Pdf Context'):
        delete_store(thread_id)
        st.session_state.pdf_name.pop(thread_id, None)

        if st.session_state.get("last_uploaded_pdf", (None, None, None))[0]==thread_id:
            st.session_state.pop("last_uploaded_pdf", None)
        st.rerun()

def side_bar():
    st.sidebar.title('AI Workspace')

    if st.sidebar.button('New Chat'):
        st.session_state.messages=[]
        st.session_state.thread_id=str(uuid.uuid4())

    st.sidebar.selectbox("model",
        options=list(Model_List.keys()),
        format_func=lambda key: Model_List[key],
        key="model")

    st.sidebar.selectbox('Assistant mode',
        options=list(assistant_mode.keys()),
        format_func=lambda key:assistant_mode[key],
        key='assistant_mode')

    handle_dataset()

    dataset_clear()

    st.sidebar.header('Chat')

    for thread_id in reversed(list(st.session_state.titles.keys())):
        title=st.session_state.titles.get(thread_id, "Untitled Chat")
        if st.sidebar.button(title, key=thread_id):
            st.session_state.thread_id=thread_id
            st.session_state.messages=load_thread_messages(thread_id)

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
            title=generate_and_save_title(thread, user_input, st.session_state.model)
            st.session_state.titles[thread]=title

        # assistance
        with st.chat_message('assistant'):
            def stream():
                for msg, _ in stream_chat(user_input, thread, st.session_state.model, st.session_state.assistant_mode):
                    if msg.content:
                        yield msg.content
            ai_text=st.write_stream(stream)
        st.session_state.messages.append({'role':'assistant','content':ai_text})