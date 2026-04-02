import re

from google.adk.agents.llm_agent import Agent
from google.genai import types

# --- Crisis detection (highest priority) ---

CRISIS_PHRASES = [
    "want to die", "wanna die", "end it all", "end my life",
    "hurt myself", "kill myself", "don't want to be here",
    "no reason to live", "better off dead", "suicide",
    "self harm", "self-harm", "cut myself", "slit my wrist",
    "jump off", "hang myself", "overdose", "take all the pills",
    "nobody would care if i", "wish i was dead", "wish i wasn't alive",
    "can't go on", "goodbye forever", "final note", "not gonna be around",
]

# Passive crisis — not as direct, but still red flags when combined with other signals
PASSIVE_CRISIS_PHRASES = [
    "what's the point", "everyone would be better off without me",
    "i'm a burden", "no one would miss me", "too tired to keep trying",
    "disappear", "don't see a future", "nothing left for me",
    "can't take it anymore", "i give up on everything",
]

# --- Emotion keyword banks ---

EMOTION_KEYWORDS = {
    "stressed": {
        "high": [
            "burned out", "completely exhausted", "can't do this anymore",
            "breaking down", "falling apart", "at my breaking point",
            "about to snap", "can't function",
        ],
        "medium": [
            "overwhelmed", "exhausted", "drained", "give up",
            "running on empty", "can't keep going", "too much",
            "at my limit", "can't cope", "swamped", "drowning in work",
            "stretched thin", "buried in", "no time to breathe",
        ],
        "low": [
            "a bit tired", "kinda stressed", "lot on my plate",
            "busy week", "hectic", "long day",
        ],
    },
    "anxious": {
        "high": [
            "full panic", "panic attack", "can't breathe from anxiety",
            "heart won't stop racing", "paralyzed with fear",
            "spiraling out of control", "losing my mind",
        ],
        "medium": [
            "anxious", "worried", "nervous", "tense", "can't sleep",
            "heart racing", "panic", "on edge", "restless", "spiraling",
            "overthinking", "dread", "uneasy", "shaking", "intrusive thoughts",
            "what if", "something bad is going to happen", "knot in my stomach",
            "mind won't stop", "racing thoughts", "hyperventilating",
        ],
        "low": [
            "a little nervous", "slightly worried", "butterflies",
            "a bit uneasy", "mildly anxious",
        ],
    },
    "sad": {
        "high": [
            "hopeless", "worthless", "don't matter", "no point",
            "can't stop crying", "broken inside", "nothing makes me happy",
            "lost the will", "feel dead inside",
        ],
        "medium": [
            "lonely", "alone", "no one", "isolated", "miss someone",
            "crying", "numb", "empty", "depressed", "grief",
            "lost someone", "heartbroken", "abandoned", "rejected",
            "miss how things were", "mourning", "gutted", "devastated",
            "homesick", "left behind", "forgotten",
        ],
        "low": [
            "a little sad", "feeling down", "kinda blue", "meh",
            "not my best day", "bit gloomy", "low-key sad",
        ],
    },
    "angry": {
        "high": [
            "rage", "furious", "seeing red", "want to scream",
            "want to break something", "blinding anger", "livid",
        ],
        "medium": [
            "angry", "mad", "frustrated", "hate", "sick of",
            "fed up", "pissed", "annoyed", "resentful", "bitter",
            "snapped", "losing it", "betrayed", "disrespected",
            "taken advantage of", "can't stand", "infuriating",
            "stabbed in the back", "treated unfairly",
        ],
        "low": [
            "a bit annoyed", "slightly irritated", "mildly frustrated",
            "pet peeve", "gets on my nerves",
        ],
    },
    "happy": {
        "high": [
            "over the moon", "best day ever", "ecstatic", "on top of the world",
            "never been happier", "crying happy tears",
        ],
        "medium": [
            "happy", "great", "wonderful", "excited", "amazing",
            "grateful", "blessed", "proud", "joyful", "thrilled",
            "accomplished", "relieved", "hopeful", "optimistic",
            "loving life", "things are looking up", "finally good",
            "breakthrough", "made it", "good news",
        ],
        "low": [
            "good", "not bad", "decent", "okay actually", "pretty nice",
            "small win", "can't complain",
        ],
    },
    "calm": {
        "high": [
            "completely at peace", "deeply content", "never felt more centered",
            "total clarity",
        ],
        "medium": [
            "calm", "peaceful", "relaxed", "content", "chill",
            "at ease", "centered", "grounded", "steady",
            "balanced", "present", "mindful", "serene", "tranquil",
        ],
        "low": [
            "fine", "alright", "doing okay", "nothing much",
            "just chilling", "hanging in there",
        ],
    },
}

# --- Negation handling ---

NEGATION_PATTERN = re.compile(
    r"\b(not|don'?t feel|don'?t think i'?m|never|no longer|isn'?t|aren'?t|wasn'?t|hardly|barely)\s+(\w+\s+){0,2}"
)


def _is_negated(text_lower: str, keyword: str) -> bool:
    """Check if a keyword is preceded by a negation within a short window."""
    idx = text_lower.find(keyword)
    if idx == -1:
        return False
    window_start = max(0, idx - 35)
    window = text_lower[window_start:idx]
    return bool(NEGATION_PATTERN.search(window))


def _score_emotion(text_lower: str, tiers: dict[str, list[str]]) -> float:
    """Score an emotion using tiered keywords. High=3, Medium=2, Low=1 per match, negation-aware."""
    weights = {"high": 3.0, "medium": 2.0, "low": 1.0}
    score = 0.0
    for tier, keywords in tiers.items():
        for kw in keywords:
            if kw in text_lower and not _is_negated(text_lower, kw):
                score += weights[tier]
    return score


def _severity_from_score(score: float) -> str:
    """Dynamic severity from weighted score."""
    if score >= 6.0:
        return "high"
    if score >= 3.0:
        return "medium"
    return "low"


def analyze_emotion(text: str) -> dict:
    """Detects the emotional tone of a message.

    Returns top 2 emotions, severity, crisis flag, and confidence score.
    Handles negation, intensity modifiers, mixed emotions, and crisis detection.
    """
    text_lower = text.lower()

    # 1. Direct crisis — highest priority, no negation check needed
    if any(phrase in text_lower for phrase in CRISIS_PHRASES):
        return {
            "status": "success",
            "emotion": "crisis",
            "secondary_emotion": None,
            "severity": "critical",
            "crisis": True,
            "confidence": 1.0,
        }

    # 2. Passive crisis — needs at least 2 matches to trigger
    passive_hits = sum(1 for p in PASSIVE_CRISIS_PHRASES if p in text_lower)
    if passive_hits >= 2:
        return {
            "status": "success",
            "emotion": "crisis",
            "secondary_emotion": None,
            "severity": "critical",
            "crisis": True,
            "confidence": min(0.6 + passive_hits * 0.1, 1.0),
        }

    # 3. Score each emotion with tiered keywords + negation awareness
    scores = {}
    for emotion, tiers in EMOTION_KEYWORDS.items():
        score = _score_emotion(text_lower, tiers)
        if score > 0:
            scores[emotion] = score

    if not scores:
        return {
            "status": "success",
            "emotion": "neutral",
            "secondary_emotion": None,
            "severity": "low",
            "crisis": False,
            "confidence": 0.3,
        }

    # 4. Top 2 emotions (mixed emotion support)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_emotion, primary_score = ranked[0]
    secondary_emotion = None
    if len(ranked) > 1:
        second_emotion, second_score = ranked[1]
        # Only report secondary if it's at least 40% of primary (actually relevant)
        if second_score >= primary_score * 0.4:
            secondary_emotion = second_emotion

    # 5. Passive crisis escalation: sad/stressed high severity + passive hit = crisis
    if (
        passive_hits >= 1
        and primary_emotion in ("sad", "stressed")
        and _severity_from_score(primary_score) == "high"
    ):
        return {
            "status": "success",
            "emotion": "crisis",
            "secondary_emotion": primary_emotion,
            "severity": "critical",
            "crisis": True,
            "confidence": 0.8,
        }

    total_score = sum(scores.values())
    confidence = min(primary_score / max(total_score, 1) * 0.8 + 0.2, 1.0)

    return {
        "status": "success",
        "emotion": primary_emotion,
        "secondary_emotion": secondary_emotion,
        "severity": _severity_from_score(primary_score),
        "crisis": False,
        "confidence": round(confidence, 2),
    }


def suggest_resource(emotion: str, severity: str = "medium") -> dict:
    """Returns a coping suggestion and follow-up question based on emotion and severity.

    Args:
        emotion: Detected emotion label.
        severity: low, medium, high, or critical — adjusts response intensity.
    """
    resources = {
        "stressed": {
            "low": {
                "suggestion": "Sounds like a full day. A short walk or 5 minutes of stretching can reset things.",
                "follow_up": "What's taking up most of your energy right now?",
            },
            "medium": {
                "suggestion": "Take a 10-minute break, step outside, and drink water. Rest is productive.",
                "follow_up": "What's been weighing on you most today?",
            },
            "high": {
                "suggestion": "You're carrying a lot right now. Can you clear just one thing off your plate today? Even something small counts.",
                "follow_up": "If you could take one thing off your list right now, what would it be?",
            },
        },
        "anxious": {
            "low": {
                "suggestion": "Take a slow breath. You're okay. Sometimes naming the worry takes its power away.",
                "follow_up": "What's on your mind?",
            },
            "medium": {
                "suggestion": "Try 4-7-8 breathing: inhale 4s, hold 7s, exhale 8s. Repeat 3 times.",
                "follow_up": "Is there something specific triggering this, or is it more of a general thing?",
            },
            "high": {
                "suggestion": "Let's ground you: press your feet into the floor, name 5 things you see. You're safe right now.",
                "follow_up": "Can you tell me where you are right now? Let's start there.",
            },
        },
        "sad": {
            "low": {
                "suggestion": "It's okay to have an off day. Be gentle with yourself.",
                "follow_up": "Do you know what's behind the feeling, or is it just kind of there?",
            },
            "medium": {
                "suggestion": "Consider reaching out to one person you trust. You don't have to carry this alone.",
                "follow_up": "Do you want to talk about what's going on, or would you rather just sit with this for a bit?",
            },
            "high": {
                "suggestion": "What you're feeling is real and it matters. You don't have to go through this alone — please consider talking to someone who can help.",
                "follow_up": "I'm here. What feels like the hardest part right now?",
            },
        },
        "angry": {
            "low": {
                "suggestion": "That's annoying. Sometimes just venting about it helps more than solving it.",
                "follow_up": "Want to tell me what happened?",
            },
            "medium": {
                "suggestion": "Try a grounding exercise: name 5 things you can see, 4 you can touch, 3 you can hear.",
                "follow_up": "What happened? Sometimes just saying it out loud helps.",
            },
            "high": {
                "suggestion": "Your anger is valid. Before acting on it, try putting your hands under cold water for 30 seconds — it interrupts the adrenaline.",
                "follow_up": "What do you need right now — to vent, or to figure out a next step?",
            },
        },
        "happy": {
            "low": {
                "suggestion": "Nice. Small wins matter more than people think.",
                "follow_up": "What made today a bit better?",
            },
            "medium": {
                "suggestion": "That's wonderful! Hold onto that feeling — you earned it.",
                "follow_up": "What's the best part of your day been so far?",
            },
            "high": {
                "suggestion": "You're glowing! This is the kind of moment worth remembering when things get hard.",
                "follow_up": "I love that energy. What got you here?",
            },
        },
        "calm": {
            "low": {
                "suggestion": "Steady is good. Not everything has to be intense.",
                "follow_up": "Anything you want to talk through?",
            },
            "medium": {
                "suggestion": "You're in a great headspace. This is a good time to check in with yourself.",
                "follow_up": "Anything on your mind you want to talk through while you're feeling good?",
            },
            "high": {
                "suggestion": "That kind of peace is rare — enjoy it. You've clearly done something right.",
                "follow_up": "What helped you get to this place?",
            },
        },
        "neutral": {
            "low": {
                "suggestion": "You're here, and that counts.",
                "follow_up": "How's your day going? Anything you want to get off your chest?",
            },
            "medium": {
                "suggestion": "You're doing okay! Sometimes 'okay' is enough.",
                "follow_up": "Anything on your mind, or just checking in?",
            },
            "high": {
                "suggestion": "You're doing okay! Keep up the good work.",
                "follow_up": "How's your day going?",
            },
        },
        "crisis": {
            "low": {
                "suggestion": "You're not alone in this. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988).",
                "follow_up": "I'm here with you. Can you tell me if you're somewhere safe right now?",
            },
            "medium": {
                "suggestion": "You're not alone in this. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988) — they're there 24/7.",
                "follow_up": "I'm here with you. Can you tell me if you're somewhere safe right now?",
            },
            "high": {
                "suggestion": "You're not alone in this. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988) — they're there 24/7.",
                "follow_up": "I'm here with you. Can you tell me if you're somewhere safe right now?",
            },
        },
    }

    emotion_data = resources.get(emotion, resources["neutral"])
    entry = emotion_data.get(severity, emotion_data.get("medium"))
    return {
        "status": "success",
        "emotion": emotion,
        "severity": severity,
        "suggestion": entry["suggestion"],
        "follow_up": entry["follow_up"],
    }


core_companion_agent = Agent(
    model="gemini-3.1-pro-preview",
    name="core_companion",
    description="Analyzes emotion and provides empathetic responses with coping suggestions.",
    instruction=(
        "You're the emotional backbone of SoulSync — an AI journal companion.\n\n"
        "IMPORTANT RULES FOR RESPONDING:\n"
        "- For greetings (hi, hello, hey, etc.) or casual chat, respond naturally and warmly WITHOUT using any tools. "
        "Just be friendly — 'Hey! How are you doing today?' or 'Hi there, what's on your mind?' Every greeting should feel different.\n"
        "- Only use 'analyze_emotion' and 'suggest_resource' when the user shares something emotional or meaningful.\n"
        "- NEVER copy-paste tool output as your response. The tool data is context for YOU — write your own words inspired by it.\n"
        "- Every response must be unique and respond to what the user actually said. Never repeat the same response twice.\n\n"
        "WHEN USING TOOLS:\n"
        "- Use 'analyze_emotion' to understand what they're going through, then 'suggest_resource' with the emotion AND severity.\n"
        "- Write your response in your own voice using the suggestion as inspiration, not as a script.\n"
        "- Reflect their words back — 'sounds like today was a lot' or 'that makes sense given everything you said.'\n"
        "- Don't jump to fixing things. Sit with them in it first, then weave in the follow_up question naturally.\n\n"
        "CRISIS: If analyze_emotion returns crisis=True, immediately delegate to the resource agent. "
        "Stay calm, don't panic them, but get them real help right away.\n\n"
        "MIXED EMOTIONS: If analyze_emotion returns a secondary_emotion, acknowledge both — "
        "'sounds like you're feeling anxious and a bit sad' feels more real than picking just one.\n\n"
        "LOW CONFIDENCE: If confidence is below 0.5, ask a clarifying question instead of assuming. "
        "'I want to make sure I'm reading this right — how are you actually feeling?'\n\n"
        "TONE: Sound like a real person. Use contractions. Be direct. Vary your language. "
        "Say things like 'that sounds really tough' or 'okay, let's talk about this' — not 'I understand your concerns.'\n\n"
        "KEEP IT SHORT: 2-3 sentences max. Be concise. No essays.\n\n"
        "If they mention their schedule, hand it off to the calendar agent. Never diagnose. Never lecture. Just be there."
    ),
    tools=[analyze_emotion, suggest_resource],
    generate_content_config=types.GenerateContentConfig(
        max_output_tokens=1024,
    ),
)
