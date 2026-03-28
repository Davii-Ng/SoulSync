import os

from google.adk.agents.llm_agent import Agent


def speak_response(response_text: str) -> dict:
    """Converts response text to audio via ElevenLabs TTS. Stub implementation."""
    # TODO: Integrate ElevenLabs API using ELEVENLABS_API_KEY from env
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "ELEVENLABS_API_KEY not set.",
        }
    # Placeholder — replace with actual ElevenLabs SDK call
    return {
        "status": "success",
        "message": f"[STUB] Audio generated for: '{response_text}'",
        "audio_url": "[STUB] https://elevenlabs.io/audio/placeholder.mp3",
    }


voice_agent = Agent(
    model="gemini-3-flash-preview",
    name="voice_agent",
    description="Converts text responses to natural-sounding audio via ElevenLabs TTS.",
    instruction=(
        "You are SoulSync's Voice Agent. Your sole responsibility is to convert text into audio. "
        "Use 'speak_response' with the final response text and return the audio output. "
        "Do not modify or interpret the text — only convert it to speech."
    ),
    tools=[speak_response],
)
