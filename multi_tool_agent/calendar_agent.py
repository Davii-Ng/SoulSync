from google.adk.agents.llm_agent import Agent


# In-memory event store (hackathon scope)
_calendar_store: list[dict] = []


def save_event(title: str, date: str) -> dict:
    """Saves an event or deadline to the internal calendar store. Stub implementation."""
    # TODO: Integrate Google Calendar API or persistent DB
    event = {"title": title, "date": date}
    _calendar_store.append(event)
    return {
        "status": "success",
        "message": f"[STUB] Saved event: '{title}' on {date}",
        "event": event,
    }


def list_events() -> dict:
    """Returns all saved events from the internal calendar store."""
    return {
        "status": "success",
        "events": _calendar_store if _calendar_store else [],
    }


calendar_agent = Agent(
    model="gemini-3-flash-preview",
    name="calendar_agent",
    description="Detects event and deadline mentions in conversation and manages an internal calendar.",
    instruction=(
        "You are SoulSync's Calendar Agent. When the user mentions an event, deadline, or appointment, "
        "use 'save_event' to store it with a title and date. "
        "If the user asks what is coming up or what they have scheduled, use 'list_events'. "
        "Keep responses brief and confirm what was saved or listed."
    ),
    tools=[save_event, list_events],
)
