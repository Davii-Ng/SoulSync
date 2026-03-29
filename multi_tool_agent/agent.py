from google.adk.agents.llm_agent import Agent
from multi_tool_agent.core_companion import core_companion_agent


def transcribe_audio(audio_input: str) -> str:
    """Listener Agent stub — converts audio to text."""
    return f"[STUB] Transcribed: '{audio_input}'"


def manage_calendar(user_text: str) -> str:
    """Calendar Agent stub — detects and saves events/deadlines."""
    return f"[STUB] Calendar action for: '{user_text}'"


def speak_response(response_text: str) -> str:
    """Voice Agent stub — converts text to audio via ElevenLabs."""
    return f"[STUB] Audio generated for: '{response_text}'"


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_orchestrator",
    description="Main orchestrator for SoulSync — routes user input through the full agent pipeline.",
    instruction=(
        "You are SoulSync's main orchestrator. Coordinate the full pipeline for every user interaction: "
        "1. Use 'transcribe_audio' to convert any audio input to text. "
        "2. Delegate the transcribed text to 'core_companion' for emotion analysis and empathetic response. "
        "3. If the user mentions events or deadlines, use 'manage_calendar' to handle them. "
        "4. Use 'speak_response' to convert the final response to audio for the user. "
        "Always maintain a warm, supportive tone. Never diagnose — only support."
    ),
    tools=[transcribe_audio, manage_calendar, speak_response],
    sub_agents=[core_companion_agent],
)