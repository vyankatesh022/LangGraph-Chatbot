from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from database import list_thread_ids,load_chat_titles,load_thread_messages,save_message, save_title

load_dotenv()

chat=None

Model_List={
    "gemini": "Gemini",
    "openai": "OpenAI",
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

def stream_chat(user_input, thread_id, provider='gemini'):
    chat_model(provider)
    save_message(thread_id, "user", user_input)
    messages=load_thread_messages(thread_id)
    state={"message": _to_langchain_messages(messages)}
    ai_message=chat.invoke(state["message"])
    text=_chunk_text(ai_message).strip()

    if text:
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