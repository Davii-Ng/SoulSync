"""Runs user messages through the ADK agent pipeline and returns the final response."""

import logging
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
    """Send a message through the ADK agent and return the final text + emotion."""
    session_id = await get_or_create_session(user_id)

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=message)],
    )

    final_text = ""
    emotion = "neutral"

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

    # If no emotion from state, try to detect from the function calls
    if emotion == "neutral" and final_text:
        from multi_tool_agent.core_companion import analyze_emotion
        result = analyze_emotion(message)
        emotion = result.get("emotion", "neutral")

    return {
        "content": final_text,
        "emotion": emotion,
    }
