# brain/hallucination_gaurd.py
def grounded_response(user_input: str) -> str | None:
    lower = (user_input or "").lower()
    impossible = [
        "did you see me", "where were you", "can you see me",
        "did you meet me", "what do i look like", "show me my picture",
        "what color is my hair", "track me", "can you hear me", "where were you yesterday"
    ]
    if any(q in lower for q in impossible):
        return ("I don’t have real-world perception like sight or hearing, "
                "so I can’t see or recall real events. But I can remember what you tell me here 💬")
    return None
