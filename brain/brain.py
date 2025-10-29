# brain/brain.py
import random

def maintain_identity(user_input: str, user_profile: dict) -> str | None:
    lowered = (user_input or "").lower()
    if any(q in lowered for q in ["what is your name", "who are you", "are you a bot"]):
        bot_name = user_profile.get("bot_name", "Zeta")
        return f"My name is {bot_name}. I'm here to help and chat with you."
    return None

def adapt_tone(user_input: str) -> dict:
    lower = (user_input or "").lower()
    if any(w in lower for w in ["i'm feeling down", "i feel sad", "i'm depressed", "i'm upset"]):
        return {"tone": "empathetic"}
    if any(w in lower for w in ["roast", "let's roast", "insult"]):
        return {"tone": "playful_roast"}
    return {"tone": "neutral"}

def natural_response(text: str, tone: str = "neutral") -> str:
    if tone == "empathetic":
        return text + " 💗 I'm listening — tell me more if you want."
    if tone == "playful_roast":
        return text + " 😏 (roast mode — keep it friendly!)"
    return text
