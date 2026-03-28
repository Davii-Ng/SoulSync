# Detects event/deadline mentions in conversation,
# saves to internal store, fetches when user asks.
# Called by Core Companion (orchestrator pattern).

from dotenv import load_dotenv
from google.adk.agents import Agent
from datetime import datetime

load_dotenv();

# In-memory event storage
# Each event is a dict: {id, title, date, time, description}
events = []

def save_event(title: str, date: str, time: str, description: str = "") -> dict:
    """Save a calendar event for the user.

    Use this tool when the user mentions an event, appointment, deadline,
    reminder, or anything to add to their schedule — even if mentioned
    briefly or casually in conversation.

    Args:
        title: Short name of the event (e.g. "Doctor appointment")
        date: Date of the event in YYYY-MM-DD format (e.g. "2026-03-30")
        time: Time of the event in HH:MM format, 24h (e.g. "15:00")
        description: Optional extra details about the event

    Returns:
        dict with status and the saved event data
    """
    event = {
        "id": len(events) + 1,
        "title": title,
        "date": date,
        "time": time,
        "description": description,
    }
    events.append(event)
    return {"status": "success", "message": f"Event '{title}' saved.", "event": event}


def get_events(date: str = "") -> dict:
    """Retrieve saved calendar events.

    Use this tool when the user asks about their schedule, upcoming events,
    or what they have planned. Also use proactively to reference the user's
    calendar when context about their schedule would help the conversation..

    Args:
        date: Optional date filter in YYYY-MM-DD format.
              If empty, returns all saved events.

    Returns:
        dict with list of matching events
    """
    if date:
        filtered = [e for e in events if e["date"] == date]
    else:
        filtered = events

    if not filtered:
        return {"status": "success", "message": "No events found.", "events": []}

    return {"status": "success", "message": f"Found {len(filtered)} event(s).", "events": filtered}