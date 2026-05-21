"""Tests for agent_runner fast path system instruction handling."""

import sys
import os
import importlib
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _load_agent_runner_real():
    """Load the real agent_runner module from file with all heavy dependencies stubbed out."""

    # Build a minimal GenerateContentConfig so the real code can call it
    class FakeConfig:
        def __init__(self, system_instruction=None, **kwargs):
            self.system_instruction = system_instruction

    genai_types_mock = MagicMock()
    genai_types_mock.GenerateContentConfig = FakeConfig

    runner_mock = MagicMock()
    session_mock = MagicMock()

    adk_runners_mock = MagicMock()
    adk_runners_mock.Runner = MagicMock(return_value=runner_mock)
    adk_sessions_mock = MagicMock()
    adk_sessions_mock.InMemorySessionService = MagicMock(return_value=session_mock)

    genai_client_mock = MagicMock()
    genai_mock = MagicMock()
    genai_mock.Client = MagicMock(return_value=genai_client_mock)

    config_mock = MagicMock()
    config_mock.GOOGLE_API_KEY = "test-key"

    stubs = {
        "multi_tool_agent": MagicMock(),
        "multi_tool_agent.agent": MagicMock(),
        "multi_tool_agent.core_companion": MagicMock(),
        "multi_tool_agent.voice_agent": MagicMock(),
        "google.adk.runners": adk_runners_mock,
        "google.adk.sessions": adk_sessions_mock,
        "google.genai.types": genai_types_mock,
        "google.genai": genai_mock,
        "app.core.config": config_mock,
    }

    # Swap in stubs, preserving originals
    original = {}
    for name, stub in stubs.items():
        original[name] = sys.modules.get(name)
        sys.modules[name] = stub

    # Use importlib to load directly from file, bypassing sys.modules cache for agent_runner
    backend_dir = Path(__file__).parent.parent
    agent_runner_path = backend_dir / "app" / "services" / "agent_runner.py"

    spec = importlib.util.spec_from_file_location(
        "app.services.agent_runner_real",
        str(agent_runner_path),
    )
    ar = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(ar)
    finally:
        # Restore original sys.modules
        for name, orig in original.items():
            if orig is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = orig

    return ar, genai_client_mock, genai_types_mock


@pytest.mark.asyncio
async def test_fast_path_passes_system_as_instruction_not_user_message():
    """_run_fast must pass system prompt via system_instruction, not as a user-role message."""
    ar, _gemini_client, _gtypes = _load_agent_runner_real()

    captured = {}

    def fake_generate(model, contents, config=None):
        captured["config"] = config
        captured["contents"] = contents
        result = MagicMock()
        result.text = "I hear you."
        return result

    # analyze_emotion and suggest_resource are imported inside _run_fast via
    # `from multi_tool_agent.core_companion import ...`, so patch the stub module.
    core_companion_stub = sys.modules.get("multi_tool_agent.core_companion")
    if core_companion_stub is None:
        core_companion_stub = MagicMock()
        sys.modules["multi_tool_agent.core_companion"] = core_companion_stub

    core_companion_stub.analyze_emotion = MagicMock(
        return_value={"emotion": "neutral", "severity": "low", "secondary_emotion": "none"}
    )
    core_companion_stub.suggest_resource = MagicMock(
        return_value={"suggestion": "breathe", "follow_up": "how are you?"}
    )

    with patch.object(ar, "_gemini") as mock_gemini:
        mock_gemini.models.generate_content.side_effect = fake_generate
        result = await ar._run_fast("I feel okay", user_id="test_user_sys_instr")

    assert result["content"] == "I hear you."

    cfg = captured.get("config")
    assert cfg is not None, "config must be passed to generate_content"
    assert cfg.system_instruction is not None, "system_instruction must be set in config"

    for msg in captured.get("contents", []):
        parts = msg.get("parts", [])
        for part in parts:
            text = part.get("text", "")
            # System prompt text must not appear as a standalone user message
            assert "You are SoulSync" not in text, (
                "System prompt must not appear in the contents list"
            )
