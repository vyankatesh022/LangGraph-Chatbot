from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from database import list_thread_ids,load_chat_titles,load_thread_messages,save_message, save_title
from rag import load_store, fetch_context

load_dotenv()

chat=None

Model_List={
    "gemini": "Gemini",
    "openai": "OpenAI",
}

assistant_mode={
    "all_in_one": "All-in-One Assistant",
    "general": "General Assistant",
    "pdf_analysis": "PDF Analysis"
}

prompts={
    "all_in_one": (
        "You are an expert AI assistant who can act as a general assistant, data analyst, "
        "data engineer, and machine learning engineer. Choose the most suitable lens for the "
        "user's request, explain tradeoffs clearly, and use uploaded data only when it is "
        "explicitly provided in the current turn context."
    ),
    "general": (
        "You are a practical AI copilot. Give clear, correct, concise help and adapt to "
        "the user's requested depth."
    ),
    "pdf_analysis": (
        "You are an expert AI assistant specialized in analyzing PDF documents. "
        "Extract key insights, summarize important sections, and adapt your analysis style "
        "based on the document type while ensuring clarity and accuracy."
    )
}

def chat_model(provider='gemini'):
    global chat
    if provider=="openai":
        from langchain_openai import ChatOpenAI
        chat=ChatOpenAI(model="gpt-4o-mini",temperature=0, max_tokens=200)
    elif provider=="gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        chat=ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0,max_tokens=50)
    return chat

class chat_state(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

def chat_node(state: chat_state):
    return {'message':[chat.invoke(state['message'])]}

def generate_and_save_title(thread_id, message, provider="gemini"):
    chat_model(provider)
    prompt=("Create a short chat title with at most 6 words for this message:\n\n" f"{message}")
    title=chat.invoke(prompt).content.strip().replace('"', "")
    save_title(thread_id, title)
    return title

def _to_langchain_messages(messages):
    chat_history=[]
    for message in messages:
        if message["role"]=="assistant":
            chat_history.append(AIMessage(content=message["content"]))
        else:
            chat_history.append(HumanMessage(content=message["content"]))
    return chat_history

def _chunk_text(chunk):
    content=getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts=[]
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                text_parts.append(item["text"])
        return "".join(text_parts)
    return str(content)

def _pdf_chat(message, thread_id):
    query=''

    for m in reversed(message):
        if m['role']=='user':
            query=m['content']
            break
    
    store=load_store(thread_id)
    context=fetch_context(query, store) if store else ''

    if context:
        pdf_message=(
            "Use the uploaded PDF content when helpful. "
            "If the answer is not in the PDF, clearly say that.\n\n"
            f"{context}")
    else:
        pdf_message="No PDF uploaded yet. Ask the user to upload one if needed."

    response=chat.invoke([SystemMessage(content=prompts['pdf_analysis']),
            SystemMessage(content=pdf_message),
            *_to_langchain_messages(message)])
    
    return _chunk_text(response).strip()

def _text_chat(message, mode):
    prompt=prompts.get(mode, prompts['general'])
    response=chat.invoke([SystemMessage(content=prompt),*_to_langchain_messages(message),])
    return _chunk_text(response).strip()

def stream_chat(user_input, thread_id, provider='gemini', assistant_mode='general'):
    chat_model(provider)
    save_message(thread_id, "user", user_input)
    message=load_thread_messages(thread_id)
    mode= assistant_mode if isinstance(assistant_mode, str) else 'general'
    text=_pdf_chat(message, thread_id) if mode=='pdf_analysis' else _text_chat(message, mode)
    
    save_message(thread_id, "assistant", text)
    yield AIMessage(content=text), None

#graph
graph=StateGraph(chat_state)

# node
graph.add_node('node',chat_node)

# edge
graph.add_edge(START,'node')
graph.add_edge('node',END)

chatbot=graph.compile()