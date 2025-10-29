# utils.py — FINAL STAN-PROOF VERSION
import os, random
from dotenv import load_dotenv
from typing import List

load_dotenv()

# memory system
from memory.memory import recall as _recall, store_memory_chunk, get_user_chroma_collection
# emotional tone, personality, and phrasing
from brain.brain import maintain_identity, adapt_tone, natural_response
# hallucination safety
from brain.hallucination_gaurd import grounded_response
# LLM backend (Gemini 2.0 Flash)
from langchain_google_genai import ChatGoogleGenerativeAI

# ===================================
# 🔹 Initialize Gemini LLM
# ===================================
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.7,
    google_api_key=GEMINI_KEY
)


# ===================================
# 🔹 Robust Recall System (safe + persistent)
# ===================================
def recall_memory(*args) -> str:
    """Enhanced recall — includes semantic and explicit fallback memory."""
    try:
        if len(args) == 2:
            user_name, query = args
            items = _recall(user_name, query, k=5)
        elif len(args) == 1:
            query = args[0]
            user_name = "default_user"
            items = _recall(user_name, query, k=5)
        else:
            return ""

        text_block = "\n".join(items) if items else ""

        # 🧠 Force-include stored explicit facts (e.g., name, city, favorites)
        col = get_user_chroma_collection(user_name)
        try:
            all_docs = col.get()
            all_texts = all_docs.get("documents", [])
            keywords = ["name", "live", "city", "from", "favorite", "like", "music", "color", "instrument"]
            explicit_facts = [t for t in all_texts if any(k in t.lower() for k in keywords)]

            for f in explicit_facts:
                if f not in text_block:
                    text_block += f"\n{f}"
        except Exception as e:
            print(f"[⚠️] recall fallback failed for {user_name}: {e}")

        return text_block.strip()
    except Exception as e:
        print(f"[⚠️] recall_memory failed: {e}")
        return ""


# ===================================
# 🔹 Store Memory Fact
# ===================================
def store_fact(user_name: str, text: str, metadata: dict | None = None):
    """Store a factual user statement persistently."""
    if not user_name:
        user_name = "unknown"
    try:
        store_memory_chunk(user_name=user_name, text=text, metadata=metadata or {"user": user_name})
    except Exception as e:
        print(f"[⚠️] Failed to store fact for {user_name}: {e}")


# ===================================
# 🔹 Extract Name Safely
# ===================================
def _extract_name_from_text(text: str) -> str | None:
    """Conservative extraction — no index errors."""
    lowered = text.lower()
    triggers = ["my name is ", "call me ", "i am ", "i'm ", "im "]
    for t in triggers:
        if t in lowered:
            parts = text.lower().split(t, 1)
            if len(parts) < 2 or not parts[1].strip():
                return None
            after = parts[1].strip()
            candidate = after.split()[0].strip(".,!?")
            if candidate.isalpha():
                return candidate.capitalize()
    return None


# ===================================
# 🤖 Chat Logic (Final)
# ===================================
def chat_with_zeta(user_input: str, user_profile: dict | None = None) -> str:
    """
    Zeta’s main chat pipeline:
      ✅ Hallucination & identity guard
      ✅ Tone adaptation
      ✅ Per-user memory recall
      ✅ Fact storage with persistence
      ✅ Natural, diverse conversation style
    """
    user_profile = user_profile or {}
    user_name = user_profile.get("name") if isinstance(user_profile, dict) else None
    lowered = user_input.lower().strip()

    # 1️⃣ Hallucination resistance
    guard_reply = grounded_response(user_input)
    if guard_reply:
        return guard_reply

    # 2️⃣ Identity consistency
    identity_reply = maintain_identity(user_input, user_profile)
    if identity_reply:
        return identity_reply

    # 3️⃣ Tone detection
    tone = adapt_tone(user_input).get("tone", "neutral")

    # 4️⃣ Recall memory context
    memory_context = recall_memory(user_name or "default_user", user_input)

    # 5️⃣ System prompt (personality + memory)
    system_prompt = (
        "You are Zeta — a warm, emotionally intelligent digital companion. "
        "Recall only verified facts shared in chat. Never invent details. "
        "Avoid repetitive greetings. Keep responses short, natural, and human-like.\n\n"
    )
    if memory_context:
        system_prompt += f"🧠 Known facts about the user:\n{memory_context}\n\n"

    full_prompt = f"{system_prompt}User: {user_input}\nZeta:"

    # 6️⃣ Generate model reply
    response = llm.invoke(full_prompt)
    resp_text = response.content if hasattr(response, "content") else str(response)
    final_reply = natural_response(resp_text.strip(), tone)

    # 7️⃣ Greeting variety
    if lowered in ["hi", "hello", "hey", "hii", "hola"]:
        greetings = [
            "Hey there! 😊 How’s everything going?",
            "Hi! Great to see you 👋",
            "Hello again! How are you feeling today?",
            "Hey! Ready for another great chat?",
            "Hi again 🌟 What’s on your mind?"
        ]
        return random.choice(greetings)

    # 8️⃣ Detect and store personal facts
    fact_triggers = [
        "my name is ", "call me ", "i live in ", "i'm from ", "i am from ",
        "my favorite ", "i like ", "my hobby ", "i play "
    ]
    if any(t in lowered for t in fact_triggers):
        extracted_name = _extract_name_from_text(user_input)
        if extracted_name and not user_name:
            user_profile["name"] = extracted_name
            user_name = extracted_name

        store_fact(user_name or "unknown", user_input.strip(), metadata={"source": "chat"})

    # 9️⃣ Backup: store confirmed model references
    if "you mentioned" in final_reply.lower() or "you told me" in final_reply.lower():
        store_fact(user_name or "unknown", final_reply.strip())

    return final_reply
