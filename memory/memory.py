# memory/memory.py — FINAL (Persistent + STAN Safe)
import os
from typing import List
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

load_dotenv()

DATA_DIR = os.path.join(os.getcwd(), "chroma_memory")
os.makedirs(DATA_DIR, exist_ok=True)

def get_embeddings():
    """Return semantic embeddings for memory."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_user_chroma_collection(user_name: str):
    """Each user gets a private, persistent Chroma namespace."""
    safe = f"user_{(user_name or 'anonymous').lower().replace(' ', '_')}"
    user_dir = os.path.join(DATA_DIR, safe)
    os.makedirs(user_dir, exist_ok=True)
    return Chroma(
        persist_directory=user_dir,
        embedding_function=get_embeddings(),
        collection_name=safe
    )

def store_memory_chunk(user_name: str, text: str, metadata: dict = None):
    """Store a fact persistently (survives app close)."""
    col = get_user_chroma_collection(user_name)
    try:
        col.add_texts([text], metadatas=[metadata or {}])
        col.persist()
    except Exception as e:
        print(f"[⚠️ Memory store failed for {user_name}: {e}]")

def recall(user_name: str, query: str, k: int = 3) -> List[str]:
    """Recall user facts using semantic + fallback keyword recall."""
    col = get_user_chroma_collection(user_name)
    try:
        if hasattr(col, "_collection") and col._collection.count() == 0:
            return []
    except Exception:
        return []
    try:
        results = col.similarity_search(query, k=k)
    except Exception:
        results = []
    # fallback: keyword-based
    try:
        all_docs = col.get()
        docs = all_docs.get("documents", [])
        keywords = ["name", "live", "city", "from", "favorite", "like", "love"]
        fallback = [d for d in docs if any(k in d.lower() for k in keywords)]
        for f in fallback:
            if f not in [r.page_content for r in results]:
                results.append(type("Doc", (), {"page_content": f}))
    except Exception:
        pass
    return [r.page_content for r in results][:k]
