import os

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

_api_key = os.getenv("ELEVENLABS_API_KEY")

# McpToolset spawns the elevenlabs-mcp server as a subprocess via uvx.
# ADK auto-discovers the MCP tools (transcribe, text_to_speech, voice_clone)
# and exposes them to the agent. The instruction constrains usage to transcribe only.
listener_agent = Agent(
    model="gemini-3-flash-preview",
    name="listener_agent",
    description="Converts user audio input to text using ElevenLabs Scribe STT via MCP.",
    instruction=(
        "You are SoulSync's Listener Agent. Your sole responsibility is to transcribe audio input into text. "
        "Use the 'transcribe' tool from ElevenLabs to convert the audio and return the transcript. "
        "Do not interpret or respond to the content — only transcribe."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["elevenlabs-mcp"],
                    env={"ELEVENLABS_API_KEY": _api_key or ""},
                ),
                timeout=30,
            ),
        ),
    ],
)
