# memory_summarizer.py
from typing import List

def summarize_texts(texts: List[str], llm) -> str:
    prompt = f"Summarize these facts briefly as memory bullets:\n\n" + "\n\n".join(texts)
    try:
        resp = llm.generate([prompt]) if hasattr(llm, "generate") else llm.invoke(prompt)
        if hasattr(resp, "generations"):
            return resp.generations[0][0].text
        return str(resp)
    except Exception:
        return "\n".join(texts[:5])
