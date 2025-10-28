# brain/personality.py
import random

def maintain_identity(user_input: str, user_profile: dict) -> str | None:
    """
    If user asks identity/probing questions, reply consistently using user_profile (e.g., name, bot_name).
    Return a short reply string if handled, otherwise None.
    """
    lowered = user_input.lower()
    if "what is your name" in lowered or "who are you" in lowered or "are you a bot" in lowered:
        bot_name = user_profile.get("bot_name", "Zeta")
        # keep it in-character and avoid "I'm an AI" phrasing if you want persona-consistency:
        return f"My name is {bot_name}. I'm here to help and chat with you."
    return None

def adapt_tone(user_input: str) -> dict:
    """
    Detect tone triggers and return dict of adjustments. Keep simple: detect 'sad','angry','joke','roast' etc.
    """
    lower = user_input.lower()
    if any(w in lower for w in ["i'm feeling down", "i feel sad", "i'm depressed", "i'm upset"]):
        return {"tone": "empathetic"}
    if any(w in lower for w in ["roast", "let's roast", "insult"]):
        return {"tone": "playful_roast"}
    return {"tone": "neutral"}

def natural_response(text: str, tone: str = "neutral") -> str:
    """Small postprocessor to adapt phrasing and add emojis sparingly."""
    if tone == "empathetic":
        return text + " 💗 I'm listening — tell me more if you want."
    if tone == "playful_roast":
        return text + " 😏 (roast mode — keep it friendly!)"
    return text
