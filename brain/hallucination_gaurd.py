# brain/hallucination_guard.py
def grounded_response(user_input: str) -> str | None:
    """
    If the user asks for private facts or impossible things, refuse gracefully.
    Return a safe reply string or None.
    """
    lower = user_input.lower()
    # examples of impossible claims
    if "did you see me yesterday" in lower or "where were you yesterday" in lower:
        return "I don't have the ability to observe real-world events or recall them unless you told me about them here. I can remember what you tell me in this chat though."
    if "what do i look like" in lower or "show me a picture" in lower:
        return "I can't see you or show pictures, but I can describe typical features or style suggestions if you tell me more."
    return None
