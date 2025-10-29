# utils.py — final hardened version
import os
import random
from dotenv import load_dotenv
from typing import List

load_dotenv()

# try import JSON fact-store helpers (fact_store.py in project root)
try:
    from fact_store import update_fact, get_fact
except Exception:
    # fallback no-op if not present
    def update_fact(user, key, value): pass
    def get_fact(user, key): return None

# memory system
from memory.memory import recall as _recall, store_memory_chunk, get_user_chroma_collection
# emotional tone, personality, and phrasing
from brain import brain as brain_module  # we import module, call functions by name
from brain.hallucination_gaurd import grounded_response
# LLM backend
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize GEMINI
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.6, google_api_key=GEMINI_KEY)

# -----------------------
# recall_memory wrapper
# -----------------------
def recall_memory(*args) -> str:
    """
    - recall_memory(user_name, query) -> per-user joined memory string
    - recall_memory(query) -> global/default collection joined string
    """
    try:
        if len(args) == 2:
            user_name, query = args
            items = _recall(user_name or "unknown", query, k=5)
            return "\n".join(items) if items else ""
        elif len(args) == 1:
            # try default_user collection
            query = args[0]
            items = _recall("default_user", query, k=5)
            return "\n".join(items) if items else ""
    except Exception:
        return ""
    return ""

# -----------------------
# store_fact wrapper
# -----------------------
def store_fact(user_name: str, text: str, metadata: dict | None = None):
    if not user_name:
        user_name = "unknown"
    try:
        store_memory_chunk(user_name=user_name, text=text, metadata=metadata or {"source": "chat"})
    except Exception as e:
        print(f"[WARNING] store_fact failed: {e}")

# -----------------------
# safe name extractor
# -----------------------
def _extract_name_from_text(text: str) -> str | None:
    lowered = text.lower()
    triggers = ["my name is ", "call me ", "i am ", "i'm ", "im "]
    for t in triggers:
        if t in lowered:
            parts = lowered.split(t, 1)
            if len(parts) < 2:
                return None
            after = parts[1].strip()
            if not after:
                return None
            candidate = after.split()[0].strip(".,!?")
            if candidate.isalpha():
                return candidate.capitalize()
    return None

# -----------------------
# main chat function
# -----------------------
def chat_with_zeta(user_input: str, user_profile: dict | None = None) -> str:
    user_profile = user_profile or {}
    user_name = user_profile.get("name") if isinstance(user_profile, dict) else None
    lowered = (user_input or "").lower().strip()

    # 1) hallucination guard first
    guard = grounded_response(user_input)
    if guard:
        return guard

    # 2) identity check
    identity = brain_module.maintain_identity(user_input, user_profile)
    if identity:
        return identity

    # 3) tone
    tone = brain_module.adapt_tone(user_input).get("tone", "neutral")

    # 4) recall
    memory_context = recall_memory(user_name or "default_user", user_input)

    # 5) build prompt
    system_prompt = (
        "You are Zeta — a warm, human-like assistant. "
        "Never claim to have seen or observed the user. "
        "If you are unsure about a fact, say you don't know. "
        "Keep replies concise, varied, and friendly.\n\n"
    )
    if memory_context:
        system_prompt += f"Known facts about the user:\n{memory_context}\n\n"

    prompt = f"{system_prompt}User: {user_input}\nAssistant:"

    # 6) call LLM
    try:
        response = llm.invoke(prompt)
        resp_text = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        # fallback safe reply if LLM call fails
        print(f"[LLM error] {e}")
        resp_text = "Sorry, I'm having trouble right now. Can we try again in a moment?"

    final = brain_module.natural_response(resp_text.strip(), tone)

    # 7) diverse greetings (avoid monotony)
    if lowered in {"hi", "hii", "hello", "hey", "hola"}:
        greetings = [
            "Hey there! 😊 How’s it going?",
            "Hi! Great to see you 👋",
            "Hello! How are you feeling today?",
            "Hey! What’s on your mind?",
            "Hi again! 🌟 Ready to chat?"
        ]
        return random.choice(greetings)

    # 8) detect explicit personal facts — conservative
    fact_triggers = ["my name is ", "call me ", "i live in ", "i'm from ", "i am from ", "my favorite ", "i like "]
    if any(t in lowered for t in fact_triggers):
        name_found = _extract_name_from_text(user_input)
        if name_found and not user_name:
            user_profile["name"] = name_found
            user_name = name_found
            # update quick JSON store
            try:
                update_fact(user_name, "name", name_found)
            except Exception:
                pass

        # store the whole utterance as memory (short conservative facts)
        try:
            store_fact(user_name or "unknown", user_input.strip(), metadata={"source": "chat"})
        except Exception:
            pass

        # try to extract city/short facts if present and update JSON quick store
        if any(x in lowered for x in ["i live in ", "i'm from ", "i am from "]):
            try:
                # simple extraction: word after 'in' or after trigger
                if "i live in" in lowered:
                    city = user_input.lower().split("i live in", 1)[1].strip().split()[0].strip(".,!?")
                elif "i'm from" in lowered or "i am from" in lowered:
                    trigger = "i'm from" if "i'm from" in lowered else "i am from"
                    city = user_input.lower().split(trigger, 1)[1].strip().split()[0].strip(".,!?")
                else:
                    city = None
                if city:
                    update_fact(user_name or "unknown", "city", city.capitalize())
            except Exception:
                pass

    # 9) direct-knowledge quick queries we can answer without LLM
    if lowered in {"what's my name", "what is my name", "tell me my name", "tell me my name?"}:
        f = get_fact(user_name or "unknown", "name")
        if f:
            return f"Your name is {f} 😊"
        # try semantic recall fallback
        rec = recall_memory(user_name or "default_user", "name")
        if rec:
            return f"I found this in my notes about you:\n{rec.splitlines()[0]}"
        return "I don't know your name yet — please tell me!"

    if lowered in {"where do i live", "where am i from", "tell me where i live"}:
        f = get_fact(user_name or "unknown", "city")
        if f:
            return f"You live in {f}."
        rec = recall_memory(user_name or "default_user", "live")
        if rec:
            return f"I found this in my notes about you:\n{rec.splitlines()[0]}"
        return "You haven't told me where you live yet!"

    return final
