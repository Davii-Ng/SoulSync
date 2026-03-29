from google.adk.agents.llm_agent import Agent
from multi_tool_agent.core_companion import core_companion_agent
from multi_tool_agent.calendar_agent import calendar_agent
from multi_tool_agent.resource_agent import resource_agent


root_agent = Agent(
    model="gemini-3-flash-preview",
    name="soulsync_orchestrator",
    description="Main orchestrator for SoulSync — routes user input to specialized sub-agents.",
    instruction=(
        "You are SoulSync, a warm and empathetic AI mental health companion. "
        "Your role is to coordinate specialized sub-agents to support the user.\n\n"
        "For every user message:\n"
        "1. Delegate to 'core_companion' for emotion analysis and an empathetic response.\n"
        "2. If the user mentions events, deadlines, or scheduling, also delegate to 'calendar_agent'.\n"
        "3. If the user shows signs of severe distress or asks for professional help, also delegate to 'resource_agent'.\n\n"
        "Always maintain a warm, supportive tone. Never diagnose — only support."
    ),
    tools=[],
    sub_agents=[core_companion_agent, calendar_agent, resource_agent],
)
