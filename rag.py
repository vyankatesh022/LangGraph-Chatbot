import os
import tempfile

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

vector_dir=os.path.join(tempfile.gettempdir(), "vectorstores")

embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_and_split_pdf(path):
    loader=PyPDFLoader(path)
    docs=loader.load()
    split=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return split.split_documents(docs)

def _store_path(thread_id):
    return os.path.join(vector_dir, thread_id)

def load_store(thread_id):
    path=_store_path(thread_id)
    if os.path.exists(path):
        return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    return None

def delete_store(thread_id):
    path=_store_path(thread_id)
    if not os.path.exists(path):
        return
    
    base=os.path.abspath(vector_dir)
    target=os.path.abspath(path)

    if not target.startswith(base):
        raise ValueError('Invalid path')

    for root, dirs, files in os.walk(target, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d))

    os.rmdir(target)   

def fetch_context(query, vectordb, k=4):
    docs=vectordb.similarity_search(query, k=k)
    return '\n\n'.join(i.page_content for i in docs)

def add_docs(thread_id, docs):
    os.makedirs(vector_dir, exist_ok=True)
    path=_store_path(thread_id)

    if os.path.exists(path):
        db=FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        db.add_documents(docs)
    else:
        db=FAISS.from_documents(docs, embeddings)
    db.save_local(path)
    return db