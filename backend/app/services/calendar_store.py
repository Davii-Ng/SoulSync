from datetime import datetime

# In-memory event storage
# Each event is a dict: {id, title, date, time, description}
events = []


def save_event(title: str, date: str, time: str = "", description: str = "") -> dict:
    """Save a calendar event for the user."""
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")
        date = parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        return {
            "status": "error",
            "message": f"Invalid date format '{date}'. Use YYYY-MM-DD (e.g. 2026-03-30).",
        }

    if time:
        try:
            parsed_time = datetime.strptime(time, "%H:%M")
            time = parsed_time.strftime("%H:%M")
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid time format '{time}'. Use HH:MM 24h (e.g. 15:00).",
            }

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
    """Retrieve saved calendar events."""
    if date:
        filtered = [e for e in events if e["date"] == date]
    else:
        filtered = events

    if not filtered:
        return {"status": "success", "message": "No events found.", "events": []}

    return {
        "status": "success",
        "message": f"Found {len(filtered)} event(s).",
        "events": filtered,
    }
