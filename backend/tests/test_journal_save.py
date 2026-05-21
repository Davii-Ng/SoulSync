"""Tests for the journal save feature — WebSocket forwarding of journal_saved signal."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_journal_saved_forwarded(client: TestClient):
    """When agent result includes journal_saved, the WS response includes it."""
    mock_agent_result = {
        "content": "Journal saved! Your conversation has been saved for today.",
        "emotion": "calm",
        "events": [],
        "journal_saved": True,
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("skip")),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "save today's journal"}))
            data = ws.receive_json()

            assert data["type"] == "text_ready"
            assert data["journal_saved"] is True
            assert data["content"] == "Journal saved! Your conversation has been saved for today."

            audio_msg = ws.receive_json()
            assert audio_msg["type"] in ("audio_ready", "audio_error")


def test_ws_no_journal_saved_when_not_triggered(client: TestClient):
    """Normal responses do not include journal_saved."""
    mock_agent_result = {
        "content": "Tell me more.",
        "emotion": "neutral",
        "events": [],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("skip")),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I had a good day"}))
            data = ws.receive_json()

            assert data["type"] == "text_ready"
            assert "journal_saved" not in data

            audio_msg = ws.receive_json()
            assert audio_msg["type"] in ("audio_ready", "audio_error")


def test_ws_journal_saved_with_audio(client: TestClient):
    """journal_saved flag coexists with audio_base64 when TTS succeeds."""
    mock_agent_result = {
        "content": "Saved! Have a great evening.",
        "emotion": "happy",
        "events": [],
        "journal_saved": True,
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", return_value=b"fake-audio"),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "that's it for today"}))
            data = ws.receive_json()

            assert data["type"] == "text_ready"
            assert data["journal_saved"] is True
            assert data["emotion"] == "happy"

            audio_msg = ws.receive_json()
            assert audio_msg["type"] == "audio_ready"
            assert "audio_base64" in audio_msg
