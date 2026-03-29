"""Runs user messages through the ADK agent pipeline and returns the final response."""

import logging
from typing import Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_tool_agent.agent import root_agent

logger = logging.getLogger(__name__)

_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent,
    app_name="soulsync",
    session_service=_session_service,
)

# Cache of user_id -> session_id
_sessions: dict[str, str] = {}


def _coerce_event_dict(raw_event: Any) -> dict[str, str] | None:
    """Normalize different calendar event shapes into the frontend contract."""
    if not isinstance(raw_event, dict):
        return None

    title = str(raw_event.get("title") or raw_event.get("name") or "").strip()
    if not title:
        return None

    date_label = str(raw_event.get("dateLabel") or "").strip()
    if not date_label:
        date = str(raw_event.get("date") or "").strip()
        time = str(raw_event.get("time") or "").strip()
        date_label = f"{date} {time}".strip() or "Upcoming"

    note = str(raw_event.get("note") or raw_event.get("description") or "").strip()
    raw_id = raw_event.get("id")
    normalized_id = str(raw_id).strip() if raw_id is not None else ""
    if not normalized_id:
        normalized_id = f"{title.lower()}|{date_label.lower()}"

    normalized: dict[str, str] = {
        "id": normalized_id,
        "title": title,
        "dateLabel": date_label,
    }
    if note:
        normalized["note"] = note
    return normalized


def _extract_events(payload: Any) -> list[dict[str, str]]:
    """Collect calendar events from nested ADK payloads."""
    if payload is None:
        return []

    found: list[dict[str, str]] = []

    if isinstance(payload, dict):
        direct = _coerce_event_dict(payload)
        if direct:
            found.append(direct)

        for key in ("event", "events", "saved_event", "calendar_event", "calendar_events"):
            if key in payload:
                found.extend(_extract_events(payload[key]))

        for nested_key in ("result", "response", "output", "data"):
            if nested_key in payload:
                found.extend(_extract_events(payload[nested_key]))

    elif isinstance(payload, list):
        for item in payload:
            found.extend(_extract_events(item))

    return found


def _dedupe_events(events: list[dict[str, str]]) -> list[dict[str, str]]:
    deduped: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for event in events:
        event_id = event.get("id", "").strip()
        if not event_id or event_id in seen_ids:
            continue
        seen_ids.add(event_id)
        deduped.append(event)

    return deduped


async def get_or_create_session(user_id: str = "default") -> str:
    """Get existing session or create a new one for the user."""
    if user_id not in _sessions:
        session = await _session_service.create_session(
            app_name="soulsync",
            user_id=user_id,
        )
        _sessions[user_id] = session.id
    return _sessions[user_id]


async def run_agent(message: str, user_id: str = "default") -> dict:
    """Send a message through the ADK agent and return text, emotion, and events."""
    session_id = await get_or_create_session(user_id)

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    final_text = ""
    emotion = "neutral"
    captured_events: list[dict[str, str]] = []

    async for event in _runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        # Collect the final agent response
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text and part.text.strip():
                    final_text = part.text

        # Try to extract emotion from tool calls in the event
        if event.actions and event.actions.state_delta:
            if "emotion" in event.actions.state_delta:
                emotion = event.actions.state_delta["emotion"]
            captured_events.extend(_extract_events(event.actions.state_delta))

        if event.content and event.content.parts:
            for part in event.content.parts:
                function_response = getattr(part, "function_response", None)
                if function_response:
                    captured_events.extend(_extract_events(function_response))

    # If no emotion from state, try to detect from the function calls
    if emotion == "neutral" and final_text:
        from multi_tool_agent.core_companion import analyze_emotion
        result = analyze_emotion(message)
        emotion = result.get("emotion", "neutral")

    deduped_events = _dedupe_events(captured_events)

    return {
        "content": final_text,
        "emotion": emotion,
        "events": deduped_events,
    }
