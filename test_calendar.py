"""Quick test script for Calendar Agent"""
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from multi_tool_agent.calendar_agent import calendar_agent

load_dotenv()

async def test():
    session_service = InMemorySessionService()
    runner = Runner(agent=calendar_agent, app_name="test", session_service=session_service)

    session = await session_service.create_session(app_name="test", user_id="test_user")

    test_messages = [
        "I have a doctor appointment on 2026-03-30 at 15:00",
        "Remind me about the hackathon demo on 2026-04-05 at 10:00",
        "What's on my schedule?",
    ]

    for msg in test_messages:
        print(f"\n{'='*50}")
        print(f"USER: {msg}")
        print(f"{'='*50}")

        from google.genai import types
        content = types.Content(role="user", parts=[types.Part.from_text(text=msg)])

        response = runner.run(user_id="test_user", session_id=session.id, new_message=content)

        for event in runner.run(user_id="test_user", session_id=session.id, new_message=content):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"AGENT: {part.text}")
                    if part.function_call:
                        print(f"TOOL CALL: {part.function_call.name}({part.function_call.args})")
                    if part.function_response:
                        print(f"TOOL RESULT: {part.function_response.response}")

asyncio.run(test())