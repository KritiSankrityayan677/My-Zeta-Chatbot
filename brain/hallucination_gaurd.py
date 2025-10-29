# brain/hallucination_gaurd.py
def grounded_response(user_input: str) -> str | None:
    """Refuses impossible or private user queries safely."""
    lower = user_input.lower()
    impossible = [
        "did you see me", "where were you", "can you see me",
        "did you meet me", "what do i look like", "show me my picture",
        "what color is my hair", "track me", "can you hear me"
    ]
    if any(q in lower for q in impossible):
        return (
            "I don’t have real-world perception like sight or hearing, "
            "so I can’t see or recall real events. "
            "But I remember everything you tell me here 💬"
        )
    return None


