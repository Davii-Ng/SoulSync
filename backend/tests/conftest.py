"""Shared fixtures — patches agent imports so tests run without API keys."""

import sys
from unittest.mock import MagicMock

# Stub out multi_tool_agent modules before any app code imports them
for mod_name in [
    "multi_tool_agent",
    "multi_tool_agent.core_companion",
    "multi_tool_agent.voice_agent",
]:
    sys.modules[mod_name] = MagicMock()

# Stub config so startup doesn't require real env vars
import os

os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-key")
