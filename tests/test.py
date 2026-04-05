from multi_tool_agent.core_companion import core_companion_agent, analyze_emotion, suggest_resource

  # Test the tools directly (no ADK/Gemini needed)
print(analyze_emotion("I'm exhausted and overwhelmed"))
print(analyze_emotion("feeling anxious about work"))
print(suggest_resource("burnout"))
print(suggest_resource("loneliness"))