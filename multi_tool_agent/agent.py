from google.adk.agents.llm_agent import Agent


def analyze_emotion(text: str) -> dict:
    """Detects the emotional tone of a message and returns a label and severity."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["burned out", "exhausted", "overwhelmed", "can't do this"]):
        return {"status": "success", "emotion": "burnout", "severity": "high"}
    if any(w in text_lower for w in ["stressed", "anxious", "worried", "nervous"]):
        return {"status": "success", "emotion": "stress", "severity": "medium"}
    if any(w in text_lower for w in ["lonely", "alone", "no one", "isolated"]):
        return {"status": "success", "emotion": "loneliness", "severity": "medium"}
    return {"status": "success", "emotion": "neutral", "severity": "low"}


def suggest_resource(emotion: str) -> dict:
    """Returns a coping suggestion based on detected emotion."""
    resources = {
        "burnout": "Take a 10-minute break, step outside, and drink water. Rest is productive.",
        "stress": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s. Repeat 3 times.",
        "loneliness": "Consider texting one person you trust, or joining a local interest group.",
        "neutral": "You're doing okay! Keep up the good work.",
    }
    return {
        "status": "success",
        "emotion": emotion,
        "suggestion": resources.get(emotion, resources["neutral"]),
    }


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_companion",
    description="An empathetic AI companion that detects emotional distress and suggests coping strategies.",
    instruction=(
        "You are SoulSync, a warm and empathetic mental health companion. "
        "When the user shares how they feel, use 'analyze_emotion' to detect their emotional state, "
        "then use 'suggest_resource' with that emotion to offer a helpful coping tip. "
        "Always respond with kindness. Never diagnose — only support."
    ),
    tools=[analyze_emotion, suggest_resource],
)