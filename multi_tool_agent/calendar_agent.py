# Detects event/deadline mentions in conversation,
# saves to internal store, fetches when user asks.
# Called by Core Companion (orchestrator pattern).

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent
from datetime import datetime

try:
    from app.services.calendar_store import get_events, save_event
except ModuleNotFoundError:
    from backend.app.services.calendar_store import get_events, save_event

load_dotenv(Path(__file__).parent.parent / ".env")

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
    model="gemini-3.1-pro-preview",
    description="Manages the user's calendar events. Saves new events and retrieves upcoming schedule when needed.",
    instruction=_build_calendar_instruction(),
    tools=[save_event, get_events],
)