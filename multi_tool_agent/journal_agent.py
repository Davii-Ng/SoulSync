from datetime import datetime
from google.adk.agents.llm_agent import Agent


# In-memory journal store
_journal_entries = []

PROMPTS = {
    "stressed": [
        "What's been weighing on you most today?",
        "If you could let go of one thing right now, what would it be?",
        "What does your body feel like when you're this stressed?",
    ],
    "anxious": [
        "What's the worst case scenario you're imagining? How likely is it really?",
        "What would you tell a friend who felt this way?",
        "What's one small thing that felt okay today?",
    ],
    "sad": [
        "What do you miss right now?",
        "When did you last feel like yourself? What was happening?",
        "Is there something you've been holding in that needs to come out?",
    ],
    "angry": [
        "What happened, and what about it felt unfair?",
        "Who or what do you really want to say something to right now?",
        "What does this anger want you to do?",
    ],
    "happy": [
        "What made today feel good? Don't let yourself skip past it.",
        "Who would you want to share this feeling with?",
        "What does this moment tell you about what you actually value?",
    ],
    "calm": [
        "What helped you get to this place?",
        "What do you want to remember about how you feel right now?",
        "What's something you've been putting off that feels approachable today?",
    ],
    "neutral": [
        "Just check in — how are you actually doing?",
        "What's been on your mind lately that you haven't said out loud?",
        "What do you want tomorrow to look like?",
    ],
}


def write_entry(content: str, emotion: str = "neutral") -> dict:
    """Save a journal entry.

    Args:
        content: What the user wants to journal about
        emotion: Detected emotion label (stressed, anxious, sad, angry, happy, calm, neutral)

    Returns:
        dict with status and the saved entry
    """
    entry = {
        "id": len(_journal_entries) + 1,
        "content": content,
        "emotion": emotion,
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }
    _journal_entries.append(entry)
    return {"status": "success", "message": "Entry saved.", "entry": entry}


def get_entries(date: str = "") -> dict:
    """Retrieve past journal entries.

    Args:
        date: Optional date filter in YYYY-MM-DD format. If empty, returns all entries.

    Returns:
        dict with list of matching entries
    """
    if date:
        filtered = [e for e in _journal_entries if e["date"] == date]
    else:
        filtered = _journal_entries

    if not filtered:
        return {"status": "success", "message": "No entries yet.", "entries": []}

    return {"status": "success", "count": len(filtered), "entries": filtered}


def get_prompt(emotion: str = "neutral") -> dict:
    """Get a reflective journaling prompt based on the user's current emotion.

    Args:
        emotion: The user's detected emotion

    Returns:
        dict with a journaling prompt
    """
    import random
    prompts = PROMPTS.get(emotion, PROMPTS["neutral"])
    return {"status": "success", "prompt": random.choice(prompts)}


journal_agent = Agent(
    model="gemini-3-flash-preview",
    name="journal_agent",
    description="Saves journal entries, retrieves past entries, and offers reflective prompts to help the user explore their thoughts.",
    instruction=(
        "You are the journaling core of SoulSync. This whole app exists so people can journal and feel heard.\n\n"
        "When someone shares something — anything — use 'write_entry' to save it. Don't wait for a perfect moment. "
        "If they're just starting and don't know what to write, use 'get_prompt' with their emotion to give them something real to respond to.\n\n"
        "When they want to look back, use 'get_entries' to pull up what they've written and reflect on it with them — "
        "notice patterns, celebrate growth, or just acknowledge how they felt.\n\n"
        "Your job isn't to solve anything. It's to help people get their thoughts out of their head and onto the page. "
        "Be curious. Ask follow-up questions. Make them feel like their words matter — because they do."
    ),
    tools=[write_entry, get_entries, get_prompt],
)
