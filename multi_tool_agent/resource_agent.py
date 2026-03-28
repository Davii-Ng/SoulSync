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
    """Returns links and tips for finding professional therapy. Stub implementation."""
    # TODO: Integrate a therapist directory API (e.g., Psychology Today, BetterHelp)
    return {
        "status": "success",
        "resources": [
            {"name": "Psychology Today Therapist Finder", "url": "[STUB] https://www.psychologytoday.com/us/therapists"},
            {"name": "BetterHelp Online Therapy", "url": "[STUB] https://www.betterhelp.com"},
            {"name": "Open Path Collective (affordable therapy)", "url": "[STUB] https://openpathcollective.org"},
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
        "You are SoulSync's Resource Agent. When a user shows signs of severe distress or asks for professional help: "
        "use 'get_crisis_resources' for emergency situations, "
        "'get_therapist_resources' to suggest finding a therapist, "
        "or 'get_mindfulness_exercise' for an immediate calming technique. "
        "Always deliver resources with warmth and without judgement. Never diagnose."
    ),
    tools=[get_crisis_resources, get_therapist_resources, get_mindfulness_exercise],
)
