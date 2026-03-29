"""WebSocket connection tests for /ws endpoint."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_connect_and_disconnect(client: TestClient):
    """Client can open and close a WebSocket connection."""
    with client.websocket_connect("/ws") as ws:
        # Connection established — just close cleanly
        pass


def test_ws_text_message_returns_response(client: TestClient):
    """Sending a text message returns a response with content and emotion."""
    mock_agent_result = {
        "content": "Keep smiling!",
        "emotion": "happy",
        "events": [],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("no TTS in test")),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I feel great today"}))
            data = ws.receive_json()

            assert data["type"] == "response"
            assert data["content"] == "Keep smiling!"
            assert data["emotion"] == "happy"
            assert "audio_base64" not in data  # TTS failed gracefully


def test_ws_text_message_with_audio(client: TestClient):
    """When TTS succeeds, response includes audio_base64."""
    mock_agent_result = {
        "content": "Take a deep breath.",
        "emotion": "calm",
        "events": [],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", return_value=b"fake-audio-bytes"),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I am relaxed"}))
            data = ws.receive_json()

            assert data["type"] == "response"
            assert data["emotion"] == "calm"
            assert "audio_base64" in data


def test_ws_empty_message_returns_error(client: TestClient):
    """Sending an empty content returns an error message."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "text", "content": ""}))
        data = ws.receive_json()

        assert data["type"] == "error"
        assert "Empty or unsupported" in data["content"]


def test_ws_agent_failure_returns_error(client: TestClient):
    """If run_agent throws, client gets a friendly error instead of disconnect."""
    with patch("app.api.routes.ws.run_agent", new=AsyncMock(side_effect=RuntimeError("agent down"))):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "hello"}))
            data = ws.receive_json()

            assert data["type"] == "error"
            assert "Something went wrong" in data["content"]


def test_ws_multiple_messages(client: TestClient):
    """Client can send multiple messages on one connection."""
    mock_agent_result = {
        "content": "I hear you.",
        "emotion": "neutral",
        "events": [],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("skip")),
    ):
        with client.websocket_connect("/ws") as ws:
            for i in range(3):
                ws.send_text(json.dumps({"type": "text", "content": f"message {i}"}))
                data = ws.receive_json()
                assert data["type"] == "response"


def test_ws_text_message_includes_events_when_returned(client: TestClient):
    """Response includes events array when agent returns calendar events."""
    mock_agent_result = {
        "content": "Got it, I saved that.",
        "emotion": "calm",
        "events": [
            {
                "id": "therapy|2026-03-31 19:30",
                "title": "Therapy check-in",
                "dateLabel": "2026-03-31 19:30",
                "note": "Captured from your conversation.",
            }
        ],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("skip")),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I have therapy Tuesday at 7:30 PM"}))
            data = ws.receive_json()

            assert data["type"] == "response"
            assert "events" in data
            assert len(data["events"]) == 1
            assert data["events"][0]["title"] == "Therapy check-in"
