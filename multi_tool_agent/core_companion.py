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
        "You are SoulSync's Core Companion, a warm and empathetic mental health companion. "
        "When the user shares how they feel, use 'analyze_emotion' to detect their emotional state, "
        "then use 'suggest_resource' with that emotion to offer a helpful coping tip. "
        "If the user mentions any events, deadlines, or calendar items, delegate to the calendar agent. "
        "If the user shows signs of severe distress or needs professional support, delegate to the resource agent. "
        "Always respond with kindness and compassion. Never diagnose — only support."
    ),
    tools=[analyze_emotion, suggest_resource],
)
