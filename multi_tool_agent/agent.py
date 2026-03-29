from google.adk.agents.llm_agent import Agent
from multi_tool_agent.core_companion import core_companion_agent
from multi_tool_agent.calendar_agent import calendar_agent
from multi_tool_agent.resource_agent import resource_agent
from multi_tool_agent.listener_agent import listener_agent
from multi_tool_agent.voice_agent import voice_agent

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_orchestrator",
    description="SoulSync's main orchestrator — analyzes emotion, responds empathetically, and delegates to specialized agents.",
    instruction=(
        "You are SoulSync, an empathetic AI mental health companion. "
        "You help people dealing with burnout, stress, and loneliness.\n\n"
        "Rules:\n"
        "- Be warm, validating, and non-judgmental\n"
        "- Keep responses concise (2-4 sentences) since they will be spoken aloud\n"
        "- Delegate to core_companion for emotion analysis and empathetic response\n"
        "- If the user mentions events, deadlines, or calendar items, delegate to calendar_agent\n"
        "- If the user shows signs of severe distress or needs professional support, delegate to resource_agent\n"
        "- If the user sends audio input, delegate to listener_agent for transcription\n"
        "- When you have a final text response to speak aloud, delegate to voice_agent\n"
        "- If someone is in crisis, gently suggest professional resources (988 Suicide & Crisis Lifeline)\n"
        "- Never diagnose conditions or prescribe medication\n"
        "- You are a supportive companion, not a replacement for professional help"
    ),
    sub_agents=[
        core_companion_agent,
        calendar_agent,
        resource_agent,
        listener_agent,
        voice_agent,
    ],
)
