"""Tests for the direct Gemini pipeline in agent_runner."""

import sys
from unittest.mock import MagicMock, patch

import os
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-key")

# Stub agent modules before any import
for mod in [
    "multi_tool_agent",
    "multi_tool_agent.core_companion",
    "multi_tool_agent.calendar_agent",
    "multi_tool_agent.resource_agent",
    "multi_tool_agent.voice_agent",
]:
    sys.modules.setdefault(mod, MagicMock())

import pytest


@pytest.mark.asyncio
async def test_run_agent_returns_content_and_emotion():
    """run_agent returns content and emotion on a normal message."""
    from app.services import agent_runner

    mock_response = MagicMock()
    mock_response.text = "That sounds really peaceful."

    with (
        patch.object(agent_runner, "analyze_emotion", return_value={
            "emotion": "calm", "severity": "low", "secondary_emotion": None, "crisis": False,
        }),
        patch.object(agent_runner, "suggest_resource", return_value={
            "suggestion": "take a breath", "follow_up": "how are you?",
        }),
        patch.object(agent_runner._gemini.models, "generate_content", return_value=mock_response),
    ):
        result = await agent_runner.run_agent("I feel calm today", user_id="u1")

    assert result["content"] == "That sounds really peaceful."
    assert result["emotion"] == "calm"
    assert result["events"] == []
    assert "journal_saved" not in result


@pytest.mark.asyncio
async def test_run_agent_sets_journal_saved_on_save_intent():
    """Messages matching the save pattern set journal_saved=True."""
    from app.services import agent_runner

    mock_response = MagicMock()
    mock_response.text = "Take care, see you next time!"

    with (
        patch.object(agent_runner, "analyze_emotion", return_value={
            "emotion": "neutral", "severity": "low", "secondary_emotion": None, "crisis": False,
        }),
        patch.object(agent_runner, "suggest_resource", return_value={"suggestion": "", "follow_up": ""}),
        patch.object(agent_runner._gemini.models, "generate_content", return_value=mock_response),
    ):
        result = await agent_runner.run_agent("that's it for today", user_id="u2")

    assert result.get("journal_saved") is True


@pytest.mark.asyncio
async def test_run_agent_passes_system_as_instruction_not_user_message():
    """System prompt must go via GenerateContentConfig.system_instruction, not contents."""
    from app.services import agent_runner

    captured: dict = {}

    def fake_generate(model, contents, config=None):
        captured["config"] = config
        captured["contents"] = contents
        r = MagicMock()
        r.text = "I hear you."
        return r

    with (
        patch.object(agent_runner, "analyze_emotion", return_value={
            "emotion": "neutral", "severity": "low", "secondary_emotion": None, "crisis": False,
        }),
        patch.object(agent_runner, "suggest_resource", return_value={"suggestion": "", "follow_up": ""}),
        patch.object(agent_runner._gemini.models, "generate_content", side_effect=fake_generate),
    ):
        await agent_runner.run_agent("I feel okay", user_id="u3")

    cfg = captured.get("config")
    assert cfg is not None, "config must be passed"
    assert cfg.system_instruction is not None, "system_instruction must be set"

    for msg in captured.get("contents", []):
        for part in msg.get("parts", []):
            assert "You are SoulSync" not in part.get("text", ""), (
                "System prompt must not appear in contents"
            )
