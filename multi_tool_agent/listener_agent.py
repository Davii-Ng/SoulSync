from google.adk.agents.llm_agent import Agent


def transcribe_audio(audio_input: str) -> dict:
    """Converts raw audio input to text via Speech-to-Text. Stub implementation."""
    # TODO: Integrate Google Speech-to-Text or Web Speech API
    return {
        "status": "success",
        "transcript": f"[STUB] Transcribed: '{audio_input}'",
    }


listener_agent = Agent(
    model="gemini-3-flash-preview",
    name="listener_agent",
    description="Converts user audio input to text for downstream processing.",
    instruction=(
        "You are SoulSync's Listener Agent. Your sole responsibility is to transcribe audio input into text. "
        "Use 'transcribe_audio' to convert the audio and return the transcript. "
        "Do not interpret or respond to the content — only transcribe."
    ),
    tools=[transcribe_audio],
)
