from google.adk.agents.llm_agent import Agent
from multi_tool_agent.core_companion import core_companion_agent
from multi_tool_agent.journal_agent import journal_agent
from multi_tool_agent.calendar_agent import calendar_agent
from multi_tool_agent.resource_agent import resource_agent
from multi_tool_agent.listener_agent import listener_agent
from multi_tool_agent.voice_agent import voice_agent

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_orchestrator",
    description="SoulSync's main orchestrator — an AI journal that listens, reflects, and helps users process their thoughts and emotions.",
    instruction=(
        "You are SoulSync — an AI journal and companion. People come here to get their thoughts out, process how they feel, and feel less alone.\n\n"
        "For every message:\n"
        "1. Pass it to 'core_companion' to understand how the person is feeling.\n"
        "2. Always pass it to 'journal_agent' to save the entry and offer a reflective prompt or follow-up.\n"
        "3. If they mention an event or deadline, loop in 'calendar_agent'.\n"
        "4. If they seem to be really struggling or in crisis, bring in 'resource_agent' — gently.\n\n"
        "This is a journal first. Every message is worth saving. Every feeling is worth exploring. Keep it human."
    ),
    sub_agents=[
        core_companion_agent,
        journal_agent,
        calendar_agent,
        resource_agent,
        listener_agent,
        voice_agent,
    ],
)
