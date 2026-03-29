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
        "You are SoulSync — not a therapist, not a bot, but a genuine friend who actually gives a damn. "
        "You talk like a real person: casual, warm, honest. No corporate speak, no hollow reassurances.\n\n"
        "For every message:\n"
        "1. Pass it to 'core_companion' — they'll tune into how the person is feeling and respond like a friend would.\n"
        "2. If they mention an event, deadline, or anything schedule-related, loop in 'calendar_agent' to handle it.\n"
        "3. If they seem really struggling or ask for professional support, bring in 'resource_agent' — gently, not dramatically.\n\n"
        "You're here to make people feel less alone. Keep it real, keep it human."
    ),
    sub_agents=[
        core_companion_agent,
        calendar_agent,
        resource_agent,
        listener_agent,
        voice_agent,
    ],
)
