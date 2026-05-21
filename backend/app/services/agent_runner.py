"""Direct Gemini pipeline — no ADK overhead on the API path.

Architecture: analyze_emotion (Python) → build prompt → one Gemini call.
Calendar intent triggers a parallel Gemini extraction call so it adds zero latency.
ADK agents (multi_tool_agent/) are unchanged and still work for `adk web`/`adk run`.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any

from google import genai
from google.genai import types as _gtypes

from multi_tool_agent.core_companion import analyze_emotion, suggest_resource
from multi_tool_agent.calendar_agent import save_event
from multi_tool_agent.resource_agent import get_crisis_resources
from app.core.config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

_gemini = genai.Client(api_key=GOOGLE_API_KEY)

_COMPANION_SYSTEM = (
    "You are SoulSync, a warm and empathetic AI journal companion. "
    "You talk like a caring friend — use contractions, be direct, keep it real. "
    "Never lecture, never diagnose, never say 'I understand your concerns.' "
    "Reflect their words back naturally, sit with them before offering anything. "
    "Keep responses concise (2-3 sentences max). "
    "If given emotion context, weave it in naturally — don't announce it. "
    "If the emotion is neutral or it's a greeting, just be friendly and warm."
)

# Per-user conversation history for the main response call
_fast_histories: dict[str, list[dict]] = {}
_MAX_FAST_HISTORY = 16  # 8 turns each side

_CALENDAR_PATTERN = re.compile(
    r"(appointment|deadline|meeting|event on|remind me|tomorrow|next\s+\w+day"
    r"|monday|tuesday|wednesday|thursday|friday|saturday|sunday"
    r"|\d{1,2}[\/\-]\d{1,2}|\d{1,2}\s+(am|pm)|at\s+\d{1,2}(:\d{2})?\s*(am|pm)?)",
    re.IGNORECASE,
)

_SAVE_PATTERN = re.compile(
    r"(save.*journal|save.*today|that'?s it for today|done for the day"
    r"|save this conversation|wrap up|end session|save chat)",
    re.IGNORECASE,
)


async def _extract_event(message: str) -> dict | None:
    """Focused Gemini call to extract structured event data from a message.

    Runs in parallel with the main response call so it adds no perceived latency.
    Returns None if no clear event is found.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    prompt = (
        f"Today is {today} ({weekday}).\n"
        f'Extract the event or appointment from: "{message}"\n\n'
        "Return JSON only. If a clear event exists:\n"
        '{"title": "short title", "date": "YYYY-MM-DD", "time": "HH:MM or empty string", "description": "optional or empty string"}\n'
        "If no clear event:\n"
        '{"title": ""}'
    )
    try:
        response = await asyncio.to_thread(
            _gemini.models.generate_content,
            model="gemini-3-flash-preview",
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config=_gtypes.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=150,
            ),
        )
        data = json.loads(response.text or "{}")
        return data if data.get("title") else None
    except Exception as e:
        logger.warning(f"Event extraction failed: {e}")
        return None


async def _call_gemini(prompt: str, user_id: str) -> str:
    """Single conversational Gemini call with bounded per-user history."""
    history = _fast_histories.setdefault(user_id, [])
    history.append({"role": "user", "parts": [{"text": prompt}]})
    if len(history) > _MAX_FAST_HISTORY:
        history[:] = history[-_MAX_FAST_HISTORY:]

    config = _gtypes.GenerateContentConfig(
        system_instruction=_COMPANION_SYSTEM,
        max_output_tokens=256,
    )
    response = await asyncio.to_thread(
        _gemini.models.generate_content,
        model="gemini-3-flash-preview",
        contents=history,
        config=config,
    )
    reply = (response.text or "").strip()

    history.append({"role": "model", "parts": [{"text": reply}]})
    if len(history) > _MAX_FAST_HISTORY:
        history[:] = history[-_MAX_FAST_HISTORY:]

    return reply or "I'm here with you. Want to share a little more?"


async def run_agent(message: str, user_id: str = "default") -> dict:
    """Single-pass pipeline: Python analysis + one Gemini call. No ADK overhead."""

    # --- Instant Python analysis (no network, no LLM) ---
    emotion_result = analyze_emotion(message)
    emotion: str = emotion_result.get("emotion", "neutral")
    severity: str = emotion_result.get("severity", "medium")
    is_crisis: bool = emotion_result.get("crisis", False)
    secondary: str = emotion_result.get("secondary_emotion") or "none"
    resource: dict = suggest_resource(emotion, severity)

    # Crisis resources are pure Python — include them in the prompt at no cost
    crisis_text = ""
    if is_crisis:
        crisis_info = get_crisis_resources()
        lines = [
            f"{r['name']}: {r['contact']}"
            for r in crisis_info.get("resources", [])[:2]
        ]
        crisis_text = "URGENT — share these with the user naturally: " + " | ".join(lines)

    # --- Build rich prompt for a single Gemini call ---
    prompt_parts = [
        f'User said: "{message}"',
        f"Emotion: {emotion} (severity: {severity}, secondary: {secondary})",
        f"Coping tip to weave in naturally: {resource.get('suggestion', '')}",
        f"Follow-up to ask naturally: {resource.get('follow_up', '')}",
    ]
    if crisis_text:
        prompt_parts.append(crisis_text)
    if _SAVE_PATTERN.search(message):
        prompt_parts.append(
            "The user wants to wrap up — acknowledge warmly and encourage them."
        )
    prompt_parts.append("Respond as a caring friend. 2-3 sentences max.")
    prompt = "\n".join(prompt_parts)

    # --- Detect intents ---
    has_calendar = bool(_CALENDAR_PATTERN.search(message))
    journal_saved = bool(_SAVE_PATTERN.search(message))

    # --- Main response + optional event extraction run in parallel ---
    if has_calendar:
        reply, event_data = await asyncio.gather(
            _call_gemini(prompt, user_id),
            _extract_event(message),
        )
    else:
        reply = await _call_gemini(prompt, user_id)
        event_data = None

    # --- Persist extracted event directly (pure Python) ---
    events: list[dict[str, Any]] = []
    if event_data:
        try:
            result = save_event(
                title=event_data["title"],
                date=event_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                time=event_data.get("time", ""),
                description=event_data.get("description", ""),
            )
            if result.get("status") == "success":
                saved = result["event"]
                date_label = saved["date"]
                if saved.get("time"):
                    date_label += f" {saved['time']}"
                events = [{
                    "id": f"{saved['title'].lower()}|{date_label.lower()}",
                    "title": saved["title"],
                    "dateLabel": date_label,
                    "note": saved.get("description", ""),
                }]
        except Exception as e:
            logger.warning(f"save_event failed: {e}")

    output: dict[str, Any] = {"content": reply, "emotion": emotion, "events": events}
    if journal_saved:
        output["journal_saved"] = True
    return output
