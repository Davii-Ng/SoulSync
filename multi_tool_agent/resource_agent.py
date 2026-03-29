from google.adk.agents.llm_agent import Agent


def get_crisis_resources() -> dict:
    """Returns emergency mental health hotlines and crisis resources."""
    return {
        "status": "success",
        "resources": [
            {"name": "988 Suicide & Crisis Lifeline", "contact": "Call or text 988"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
            {"name": "NAMI Helpline", "contact": "1-800-950-6264"},
        ],
    }


def get_therapist_resources() -> dict:
    """Returns links and tips for finding professional therapy."""
    return {
        "status": "success",
        "resources": [
            {"name": "Psychology Today Therapist Finder", "url": "https://www.psychologytoday.com/us/therapists"},
            {"name": "BetterHelp Online Therapy", "url": "https://www.betterhelp.com"},
            {"name": "Open Path Collective (affordable therapy)", "url": "https://openpathcollective.org"},
        ],
    }


def get_mindfulness_exercise() -> dict:
    """Returns a short mindfulness or grounding exercise."""
    return {
        "status": "success",
        "exercise": (
            "Try the 5-4-3-2-1 grounding technique: name 5 things you can see, "
            "4 you can touch, 3 you can hear, 2 you can smell, 1 you can taste."
        ),
    }


resource_agent = Agent(
    model="gemini-3-flash-preview",
    name="resource_agent",
    description="Provides mental health resources, crisis hotlines, therapist referrals, and mindfulness exercises.",
    instruction=(
        "You step in when someone really needs it — not with alarm, but with care. "
        "If they're in crisis, use 'get_crisis_resources' and share those numbers like a friend would: gently, matter-of-factly, no panic. "
        "If they're open to talking to someone professionally, use 'get_therapist_resources' — frame it as a normal, good thing to do, not a last resort. "
        "If they just need to breathe right now, use 'get_mindfulness_exercise' and walk them through it like you're right there with them. "
        "Never make them feel broken for struggling. No judgement, no labels, no diagnosis. Just support."
    ),
    tools=[get_crisis_resources, get_therapist_resources, get_mindfulness_exercise],
)
