# memory/storage.py
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.getcwd(), "data", "chroma")
os.makedirs(DATA_DIR, exist_ok=True)

# Create embeddings once
def get_embeddings():
    # choose a local HF model that you installed; or use a lightweight one
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_chroma_collection(collection_name: str = "zeta_memories"):
    embeddings = get_embeddings()
    # Persistent Chroma using default local persistence implementation in langchain
    return Chroma(persist_directory=DATA_DIR, embedding_function=embeddings, collection_name=collection_name)

# store memory chunk (only when it is a 'fact' or important)
def store_memory_chunk(text: str, metadata: dict = None, collection_name: str = "zeta_memories"):
    col = get_chroma_collection(collection_name)
    col.add_texts([text], metadatas=[metadata or {}], ids=None)
    col.persist()

# recall top-k memory chunks relevant to query
def recall(query: str, k: int = 3, collection_name: str = "zeta_memories") -> List[str]:
    col = get_chroma_collection(collection_name)
    if col._collection.count() == 0:
        return []
    results = col.similarity_search(query, k=k)
    return [r.page_content for r in results]

# optional: list all memory (debug)
def list_all(collection_name: str = "zeta_memories"):
    col = get_chroma_collection(collection_name)
    docs = col.get()
    return docs
