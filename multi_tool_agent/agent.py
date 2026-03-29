from google.adk.agents.llm_agent import Agent
from multi_tool_agent.core_companion import core_companion_agent
from multi_tool_agent.calendar_agent import calendar_agent
from multi_tool_agent.resource_agent import resource_agent

root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_orchestrator",
    description="SoulSync's main orchestrator — an AI journal that listens, reflects, and helps users process their thoughts and emotions.",
    instruction=(
        "You are SoulSync's orchestrator. You NEVER respond to the user directly. "
        "Your ONLY job is to route messages to the right sub-agent.\n\n"
        "EVERY single user message — no exceptions — must be transferred to 'core_companion'. "
        "Do NOT answer, greet, or respond yourself. Always transfer.\n\n"
        "Additional routing rules:\n"
        "- If the user mentions an event, deadline, or schedule, also transfer to 'calendar_agent'.\n"
        "- If the user seems in crisis or severe distress, also transfer to 'resource_agent'.\n\n"
        "You are a router, not a responder. Never generate your own reply."
    ),
    sub_agents=[
        core_companion_agent,
        calendar_agent,
        resource_agent,
    ],
)
