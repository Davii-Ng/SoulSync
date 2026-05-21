"""Shared fixtures — stubs heavy agent imports so tests run without API keys."""

import sys
from unittest.mock import MagicMock

import os
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-key")

# Stub all multi_tool_agent sub-modules before app code imports them
for mod_name in [
    "multi_tool_agent",
    "multi_tool_agent.core_companion",
    "multi_tool_agent.calendar_agent",
    "multi_tool_agent.resource_agent",
    "multi_tool_agent.voice_agent",
]:
    sys.modules[mod_name] = MagicMock()
