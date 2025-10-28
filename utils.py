# utils.py
# utils.py

from memory.memory import recall, store_memory_chunk
from brain.brain import maintain_identity, adapt_tone, natural_response
from brain.hallucination_gaurd import grounded_response
from dotenv import load_dotenv
import os
load_dotenv()

# your LLM initialization — make sure it runs once in this module
from langchain_google_genai import ChatGoogleGenerativeAI
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")

# init llm (adjust model string to one available in your account)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, google_api_key= os.getenv("GEMINI_API_KEY")
 )

def recall_memory(query: str) -> str:
    items = recall(query, k=3)
    return "\n".join(items) if items else ""

def store_fact(user_input: str, note: str, metadata: dict = None):
    # simple rule: store if note flagged as fact (from your app logic)
    store_memory_chunk(note, metadata=metadata)

def chat_with_zeta(user_input: str, user_profile: dict = None) -> str:
    # 1) identity / hallucination checks
    identity = maintain_identity(user_input, user_profile or {})
    if identity:
        return identity
    guard = grounded_response(user_input)
    if guard:
        return guard

    # 2) tone adaptation
    tone_dict = adapt_tone(user_input)
    tone = tone_dict.get("tone", "neutral")

    # 3) recall a few relevant facts
    past = recall_memory(user_input)

    # 4) construct prompt
    system = f"You are Zeta, a friendly assistant. Keep personality consistent. Known user facts:\n{past}\n"
    prompt = f"{system}\nUser: {user_input}\nAssistant:"

    # 5) ask model
    response = llm.invoke(prompt)
    resp_text = response.content if hasattr(response, "content") else str(response)

    # 6) naturalize to match tone, and store if short user revealed a fact (simple heuristic)
    final = natural_response(resp_text.strip(), tone)

    # Simple heuristic: if user told a personal fact (e.g., 'my name is X', 'i live in ...'), store it
    lowered = user_input.lower()
    if any(p in lowered for p in ["my name is ", "i live in ", "my favorite", "i'm from", "i am from"]):
        # store short fact chunk
        store_fact(user_input, user_input, metadata={"user": user_profile.get("user_id") if user_profile else "unknown"})

    return final

