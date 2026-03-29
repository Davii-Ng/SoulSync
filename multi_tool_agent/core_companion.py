import re

from google.adk.agents.llm_agent import Agent

CRISIS_PHRASES = [
    "want to die", "wanna die", "end it all", "end my life",
    "hurt myself", "kill myself", "don't want to be here",
    "no reason to live", "better off dead", "suicide",
    "self harm", "self-harm", "cut myself",
]

EMOTION_KEYWORDS = {
    "stressed": [
        "burned out", "exhausted", "overwhelmed", "can't do this", "give up",
        "drained", "running on empty", "can't keep going", "breaking down",
        "too much", "falling apart", "at my limit", "can't cope",
    ],
    "anxious": [
        "stressed", "anxious", "worried", "nervous", "tense",
        "can't sleep", "heart racing", "panic", "on edge", "restless",
        "spiraling", "overthinking", "dread", "uneasy", "shaking",
    ],
    "sad": [
        "lonely", "alone", "no one", "isolated", "miss someone",
        "crying", "numb", "empty", "hopeless", "worthless",
        "don't matter", "no point", "depressed", "grief", "lost someone",
    ],
    "angry": [
        "angry", "furious", "mad", "frustrated", "rage",
        "hate", "sick of", "fed up", "pissed", "annoyed",
        "resentful", "bitter", "snapped", "losing it",
    ],
    "happy": [
        "happy", "great", "wonderful", "excited", "amazing", "good",
        "grateful", "blessed", "proud", "joyful", "thrilled",
        "accomplished", "relieved", "hopeful", "optimistic",
    ],
    "calm": [
        "calm", "peaceful", "relaxed", "content", "fine",
        "chill", "at ease", "centered", "grounded", "steady",
    ],
}

NEGATION_PATTERN = re.compile(
    r"\b(not|don'?t feel|don'?t think i'?m|never|no longer|isn'?t|aren'?t|wasn'?t)\s+(\w+\s+){0,2}"
)


def _is_negated(text_lower: str, keyword: str) -> bool:
    """Check if a keyword is preceded by a negation within a short window."""
    idx = text_lower.find(keyword)
    if idx == -1:
        return False
    window_start = max(0, idx - 30)
    window = text_lower[window_start:idx]
    return bool(NEGATION_PATTERN.search(window))


def _count_matches(text_lower: str, keywords: list[str]) -> int:
    """Count non-negated keyword matches."""
    return sum(
        1 for kw in keywords
        if kw in text_lower and not _is_negated(text_lower, kw)
    )


def _severity_from_count(count: int) -> str:
    """Dynamic severity: 1=low, 2-3=medium, 4+=high."""
    if count >= 4:
        return "high"
    if count >= 2:
        return "medium"
    return "low"


def analyze_emotion(text: str) -> dict:
    """Detects the emotional tone of a message. Returns top emotions, severity, and crisis flag."""
    text_lower = text.lower()

    # 1. Crisis detection — highest priority
    if any(phrase in text_lower for phrase in CRISIS_PHRASES):
        return {
            "status": "success",
            "emotion": "crisis",
            "secondary_emotion": None,
            "severity": "critical",
            "crisis": True,
        }

    # 2. Score each emotion with negation awareness
    scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = _count_matches(text_lower, keywords)
        if count > 0:
            scores[emotion] = count

    if not scores:
        return {
            "status": "success",
            "emotion": "neutral",
            "secondary_emotion": None,
            "severity": "low",
            "crisis": False,
        }

    # 3. Top 2 emotions (mixed emotion support)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_emotion, primary_count = ranked[0]
    secondary_emotion = ranked[1][0] if len(ranked) > 1 else None

    return {
        "status": "success",
        "emotion": primary_emotion,
        "secondary_emotion": secondary_emotion,
        "severity": _severity_from_count(primary_count),
        "crisis": False,
    }


def suggest_resource(emotion: str) -> dict:
    """Returns a coping suggestion and follow-up question based on detected emotion."""
    resources = {
        "stressed": {
            "suggestion": "Take a 10-minute break, step outside, and drink water. Rest is productive.",
            "follow_up": "What's been weighing on you most today?",
        },
        "anxious": {
            "suggestion": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s. Repeat 3 times.",
            "follow_up": "Is there something specific that's making you feel this way, or is it more of a general thing?",
        },
        "sad": {
            "suggestion": "Consider texting one person you trust, or joining a local interest group.",
            "follow_up": "Do you want to talk about what's going on, or would you rather just sit with this for a bit?",
        },
        "angry": {
            "suggestion": "Try a grounding exercise: name 5 things you can see, 4 you can touch, 3 you can hear.",
            "follow_up": "What happened? Sometimes just saying it out loud helps.",
        },
        "happy": {
            "suggestion": "That's wonderful! Keep doing what brings you joy.",
            "follow_up": "What's the best part of your day been so far?",
        },
        "calm": {
            "suggestion": "You're in a great headspace. Keep up the good work!",
            "follow_up": "Anything on your mind you want to talk through while you're feeling good?",
        },
        "neutral": {
            "suggestion": "You're doing okay! Keep up the good work.",
            "follow_up": "How's your day going? Anything you want to get off your chest?",
        },
        "crisis": {
            "suggestion": "You're not alone in this. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988) — they're there 24/7.",
            "follow_up": "I'm here with you. Can you tell me if you're somewhere safe right now?",
        },
    }
    entry = resources.get(emotion, resources["neutral"])
    return {
        "status": "success",
        "emotion": emotion,
        "suggestion": entry["suggestion"],
        "follow_up": entry["follow_up"],
    }


core_companion_agent = Agent(
    model="gemini-3-flash-preview",
    name="core_companion",
    description="Analyzes emotion and provides empathetic responses with coping suggestions.",
    instruction=(
        "You're the emotional backbone of SoulSync — an AI journal. Your job is to read what someone wrote and actually feel it.\n\n"
        "Use 'analyze_emotion' to understand what they're really going through, then 'suggest_resource' to offer something grounded. "
        "Reflect their words back — 'sounds like today was a lot' or 'that makes sense given everything you said.' "
        "Don't jump to fixing things. Sit with them in it first, then offer the follow_up question to keep them writing.\n\n"
        "CRITICAL: If analyze_emotion returns crisis=True, immediately delegate to the resource agent. "
        "Stay calm, don't panic them, but get them real help right away.\n\n"
        "If analyze_emotion returns a secondary_emotion, acknowledge both — 'sounds like you're feeling anxious and a bit sad' "
        "feels more real than picking just one.\n\n"
        "Sound like a person who genuinely read what they wrote. Use contractions. Be direct. "
        "Say things like 'that sounds really tough' or 'okay, let's talk about this' — not 'I understand your concerns.'\n\n"
        "If they mention their schedule, hand it off to the calendar agent. Never diagnose. Never lecture. Just be there."
    ),
    tools=[analyze_emotion, suggest_resource],
)
