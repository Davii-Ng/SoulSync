# Detects event/deadline mentions in conversation,
# saves to internal store, fetches when user asks.
# Called by Core Companion (orchestrator pattern).

from dotenv import load_dotenv
from google.adk.agents import Agent
from datetime import datetime

load_dotenv()

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
    calendar when context about their schedule would help the conversation.

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


calendar_agent = Agent(
    name="calendar_agent",
    model="gemini-2.0-flash",
    description="Manages the user's calendar events. Saves new events and retrieves upcoming schedule when needed.",
    instruction="""You are the Calendar Agent for SoulSync, a mental health companion.
Your job is to help manage the user's schedule and events.

When the user mentions an event, appointment, deadline, or reminder:
- Extract the title, date, time, and any description
- Use save_event to store it
- Confirm back to the user what was saved

When the user asks about their schedule or you need calendar context:
- Use get_events to retrieve relevant events
- Summarize clearly and concisely

Always be warm and supportive in tone — you are part of a mental health companion.
If the user gives incomplete info (e.g. no time), do your best to save what you have.
Use YYYY-MM-DD for dates and HH:MM 24h format for times.
""",
    tools=[save_event, get_events],
)