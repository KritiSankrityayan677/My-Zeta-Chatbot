# memory/summarizer.py
from typing import List
from langchain.chat_models import ChatOpenAI  # or your llm wrapper
from langchain.prompts import ChatPromptTemplate

# small summarizer that compresses a bunch of texts into one summary string
def summarize_texts(texts: List[str], llm) -> str:
    prompt = f"Summarize these facts briefly and keep them as user-memory bullets:\n\n" + "\n\n".join(texts)
    resp = llm.generate([prompt]) if hasattr(llm, "generate") else llm.invoke(prompt)
    if hasattr(resp, "generations"):
        return resp.generations[0][0].text
    # fallback
    return str(resp)
