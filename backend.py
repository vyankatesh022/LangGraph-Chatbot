from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from database import list_thread_ids,load_chat_titles,load_thread_messages,save_message, save_title

load_dotenv()

chat= ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0,
    max_tokens=50)

class chat_state(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

def chat_node(state: chat_state):
    return {'message':[chat.invoke(state['message'])]}

def generate_title(message):
    prompt=(
        f'''create a short chat title (max 6 words).
          summarizing the following message :\n\n
          {message}'''
    )
    return chat.invoke(prompt).content.strip().replace('"', '')

def generate_and_save_title(thread_id, message):
    title=generate_title(message)
    save_title(thread_id, title)
    return title

def _to_langchain_messages(messages):
    chat_history=[]
    for message in messages:
        if message["role"] == "assistant":
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

def stream_chat(user_input, thread_id):
    save_message(thread_id, "user", user_input)
    messages=load_thread_messages(thread_id)
    state={"message": _to_langchain_messages(messages)}
    result=chatbot.invoke(state, config={"configurable": {"thread_id": str(thread_id)}})
    ai_message=result["message"][-1]
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