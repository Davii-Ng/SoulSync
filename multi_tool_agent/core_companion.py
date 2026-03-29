from google.adk.agents.llm_agent import Agent


def analyze_emotion(text: str) -> dict:
    """Detects the emotional tone of a message and returns a label and severity."""
    text_lower = text.lower()
    if any(w in text_lower for w in ["burned out", "exhausted", "overwhelmed", "can't do this", "give up"]):
        return {"status": "success", "emotion": "stressed", "severity": "high"}
    if any(w in text_lower for w in ["stressed", "anxious", "worried", "nervous", "tense"]):
        return {"status": "success", "emotion": "anxious", "severity": "medium"}
    if any(w in text_lower for w in ["lonely", "alone", "no one", "isolated", "miss someone"]):
        return {"status": "success", "emotion": "sad", "severity": "medium"}
    if any(w in text_lower for w in ["angry", "furious", "mad", "frustrated", "rage"]):
        return {"status": "success", "emotion": "angry", "severity": "medium"}
    if any(w in text_lower for w in ["happy", "great", "wonderful", "excited", "amazing", "good"]):
        return {"status": "success", "emotion": "happy", "severity": "low"}
    if any(w in text_lower for w in ["calm", "peaceful", "relaxed", "content", "fine"]):
        return {"status": "success", "emotion": "calm", "severity": "low"}
    return {"status": "success", "emotion": "neutral", "severity": "low"}


def suggest_resource(emotion: str) -> dict:
    """Returns a coping suggestion based on detected emotion."""
    resources = {
        "stressed": "Take a 10-minute break, step outside, and drink water. Rest is productive.",
        "anxious": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s. Repeat 3 times.",
        "sad": "Consider texting one person you trust, or joining a local interest group.",
        "angry": "Try a grounding exercise: name 5 things you can see, 4 you can touch, 3 you can hear.",
        "happy": "That's wonderful! Keep doing what brings you joy.",
        "calm": "You're in a great headspace. Keep up the good work!",
        "neutral": "You're doing okay! Keep up the good work.",
    }
    return {
        "status": "success",
        "emotion": emotion,
        "suggestion": resources.get(emotion, resources["neutral"]),
    }


core_companion_agent = Agent(
    model="gemini-3-flash-preview",
    name="core_companion",
    description="Analyzes emotion and provides empathetic responses with coping suggestions.",
    instruction=(
        "You're the heart of SoulSync — a friend who listens first and talks second. "
        "When someone opens up, use 'analyze_emotion' to understand what they're going through, "
        "then 'suggest_resource' to offer something actually useful — not generic advice, real talk.\n\n"
        "Sound like a person, not a help desk. Use contractions. Be direct. Acknowledge what they said before jumping in. "
        "Say things like 'that sounds really tough' or 'okay, let's figure this out together' — not 'I understand your concerns.' "
        "If they mention something on their calendar, hand it off to the calendar agent. "
        "If they're really struggling, bring in the resource agent — but ease into it, don't make it a big deal. "
        "Never diagnose. Never lecture. Just be there."
    ),
    tools=[analyze_emotion, suggest_resource],
)
