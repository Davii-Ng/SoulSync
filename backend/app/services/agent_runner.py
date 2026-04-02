"""Runs user messages through the ADK agent pipeline and returns the final response."""

import re
import logging
import importlib
from typing import Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from multi_tool_agent.agent import root_agent
from multi_tool_agent.core_companion import core_companion_agent

logger = logging.getLogger(__name__)

_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent,
    app_name="soulsync",
    session_service=_session_service,
)
_fast_runner = Runner(
    agent=core_companion_agent,
    app_name="soulsync_fast",
    session_service=_session_service,
)

# Patterns that need the full orchestrator (calendar, crisis, journal-save)
_ORCHESTRATOR_PATTERNS = re.compile(
    r"(save.*journal|that'?s it for today|done for the day|save this conversation|wrap up|end session"
    r"|appointment|deadline|schedule|meeting|event on|remind me"
    r"|want to die|kill myself|end it all|end my life|hurt myself|suicide|self.harm"
    r"|therapist|therapy|counselor|crisis|hotline|helpline|real help|real person"
    r"|what'?s on my calendar|what do i have|upcoming events)",
    re.IGNORECASE,
)


def _needs_orchestrator(message: str) -> bool:
    """Check if message needs full orchestrator routing."""
    return bool(_ORCHESTRATOR_PATTERNS.search(message))

# Cache of user_id -> session_id
_sessions: dict[str, str] = {}

# Track turn count per user to rotate sessions before context overflows
_turn_counts: dict[str, int] = {}
_MAX_TURNS = 15  # Rotate session after this many exchanges


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


async def get_or_create_session(user_id: str = "default", app_name: str = "soulsync") -> str:
    """Get existing session or create a new one for the user.

    Rotates the session after _MAX_TURNS exchanges to prevent the ADK
    context window from filling up (which causes truncated model responses).
    """
    key = f"{user_id}:{app_name}"
    turns = _turn_counts.get(key, 0)
    if key in _sessions and turns >= _MAX_TURNS:
        logger.info(f"Rotating session for {key} after {turns} turns")
        del _sessions[key]
        _turn_counts[key] = 0

    if key not in _sessions:
        session = await _session_service.create_session(
            app_name=app_name,
            user_id=user_id,
        )
        _sessions[key] = session.id
        _turn_counts[key] = 0

    return _sessions[key]


async def run_agent(message: str, user_id: str = "default") -> dict:
    """Send a message through the ADK agent and return text, emotion, and events.

    Uses a fast path (direct to core_companion, skip orchestrator) for normal
    messages. Falls back to full orchestrator for calendar, crisis, and
    journal-save triggers.
    """
    use_orchestrator = _needs_orchestrator(message)
    runner = _runner if use_orchestrator else _fast_runner
    app_name = "soulsync" if use_orchestrator else "soulsync_fast"

    session_id = await get_or_create_session(user_id, app_name=app_name)

    # Run local emotion analysis upfront (no Gemini call)
    from multi_tool_agent.core_companion import analyze_emotion, suggest_resource
    emotion_result = analyze_emotion(message)
    emotion = emotion_result.get("emotion", "neutral")
    severity = emotion_result.get("severity", "medium")

    calendar_events_before: list[Any] = []
    calendar_module = None
    if use_orchestrator:
        try:
            calendar_module = importlib.import_module("multi_tool_agent.calendar_agent")
            maybe_events = getattr(calendar_module, "events", [])
            if isinstance(maybe_events, list):
                calendar_events_before = list(maybe_events)
        except Exception:
            calendar_module = None

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    final_text = ""
    captured_events: list[dict[str, str]] = []
    journal_saved = False

    async for event in runner.run_async(
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
                    # Detect save_journal tool signal
                    resp_data = getattr(function_response, "response", None)
                    if isinstance(resp_data, dict) and resp_data.get("journal_saved"):
                        journal_saved = True

    # Increment turn counter for session rotation
    key = f"{user_id}:{app_name}"
    _turn_counts[key] = _turn_counts.get(key, 0) + 1

    # Fallback: read calendar in-memory store in case ADK event payload omits tool outputs.
    if calendar_module is not None:
        maybe_events = getattr(calendar_module, "events", [])
        if isinstance(maybe_events, list):
            new_events = maybe_events[len(calendar_events_before):]
            captured_events.extend(_extract_events(new_events))
            captured_events.extend(_extract_events(maybe_events))

    deduped_events = _dedupe_events(captured_events)

    result: dict[str, Any] = {
        "content": final_text,
        "emotion": emotion,
        "events": deduped_events,
    }
    if journal_saved:
        result["journal_saved"] = True
    return result
