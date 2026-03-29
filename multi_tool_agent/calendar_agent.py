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

def save_event(title: str, date: str, time: str = "", description: str = "") -> dict:
    """Save a calendar event for the user.

    Use this tool when the user mentions an event, appointment, deadline,
    reminder, or anything to add to their schedule — even if mentioned
    briefly or casually in conversation.

    Args:
        title: Short name of the event (e.g. "Doctor appointment")
        date: Date of the event in YYYY-MM-DD format (e.g. "2026-03-30").
              Must be a valid date. Use today's date from the instruction
              to resolve relative dates like "tomorrow" or "next Monday".
        time: Time of the event in HH:MM format, 24h (e.g. "15:00").
              Optional — leave empty if the user didn't mention a time.
        description: Optional extra details about the event

    Returns:
        dict with status and the saved event data
    """
    # Validate date format
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        date = parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return {"status": "error", "message": f"Invalid date format '{date}'. Use YYYY-MM-DD (e.g. 2026-03-30)."}

    # Validate time format if provided
    if time:
        try:
            parsed_time = datetime.strptime(time, "%H:%M")
            time = parsed_time.strftime("%H:%M")
        except ValueError:
            return {"status": "error", "message": f"Invalid time format '{time}'. Use HH:MM 24h (e.g. 15:00)."}

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
    model="gemini-3.1-pro-preview",
    description="Manages the user's calendar events. Saves new events and retrieves upcoming schedule when needed.",
    instruction="""You're the one who keeps track of things so the user doesn't have to stress about it.
def _build_calendar_instruction() -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    return f"""You're the one who keeps track of things so the user doesn't have to stress about it.
When they mention anything — an appointment, a deadline, a thing they have to do — just save it. Don't make it a whole thing.

**TODAY'S DATE: {today} ({weekday})**

Use today's date to resolve relative dates:
- "today" → {today}
- "tomorrow" → use the day after {today}
- "next Monday" → find the next Monday after {today}
- If the user gives a specific date like "March 30" or "3/30", convert it to YYYY-MM-DD format using the current year (2026) unless they specify otherwise.
- If the user gives a specific date AND time, use EXACTLY what they say — do not change or guess differently.

Pick up the title, date, time, and any details from what they said. Use save_event to store it, then confirm casually — like "got it, I've added that for you." Include the saved date and time in your confirmation so the user can verify it's correct.

If they ask what's coming up or you think their schedule is relevant, use get_events and give them a quick, friendly rundown.

Keep the vibe relaxed. You're a friend helping them stay organized, not a personal assistant reading from a script.
If info is missing (like no time), just save what you have — don't make them repeat themselves.
Dates MUST go in YYYY-MM-DD format, times in HH:MM 24h format.
"""


calendar_agent = Agent(
    name="calendar_agent",
    model="gemini-3-flash-preview",
    description="Manages the user's calendar events. Saves new events and retrieves upcoming schedule when needed.",
    instruction=_build_calendar_instruction(),
    tools=[save_event, get_events],
)