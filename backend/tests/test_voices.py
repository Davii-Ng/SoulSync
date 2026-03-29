"""Tests for voice selection endpoints and WebSocket voice preference."""

import json
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


# --- GET /voices ---


def test_get_voices_returns_list(client: TestClient):
    """GET /voices returns a list of voice objects with voice_id and name."""
    mock_voices = [
        {"voice_id": "abc123", "name": "Rachel"},
        {"voice_id": "def456", "name": "Adam"},
    ]

    with patch("app.api.routes.speech.get_available_voices", new=AsyncMock(return_value=mock_voices)):
        response = client.get("/voices")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["voices"]) == 2
    assert data["voices"][0]["voice_id"] == "abc123"
    assert data["voices"][1]["name"] == "Adam"


def test_get_voices_handles_error(client: TestClient):
    """GET /voices returns 502 when ElevenLabs call fails."""
    with patch("app.api.routes.speech.get_available_voices", new=AsyncMock(side_effect=RuntimeError("no key"))):
        response = client.get("/voices")

    assert response.status_code == 502
    data = response.json()
    assert data["success"] is False


# --- POST /voices/preview ---


def test_voice_preview_returns_audio(client: TestClient):
    """POST /voices/preview returns MP3 audio bytes for the given voice_id."""
    with patch("app.api.routes.speech.text_to_speech", return_value=b"fake-mp3-bytes"):
        response = client.post("/voices/preview", json={"voice_id": "abc123"})

    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/mpeg"
    assert response.content == b"fake-mp3-bytes"
    assert int(response.headers["content-length"]) == len(b"fake-mp3-bytes")


def test_voice_preview_passes_voice_id(client: TestClient):
    """POST /voices/preview calls text_to_speech with the requested voice_id."""
    mock_tts = MagicMock(return_value=b"audio")

    with patch("app.api.routes.speech.text_to_speech", mock_tts):
        client.post("/voices/preview", json={"voice_id": "custom_voice"})

    mock_tts.assert_called_once()
    _, kwargs = mock_tts.call_args
    assert kwargs["voice_id"] == "custom_voice"


def test_voice_preview_handles_error(client: TestClient):
    """POST /voices/preview returns 502 when TTS fails."""
    with patch("app.api.routes.speech.text_to_speech", side_effect=RuntimeError("TTS down")):
        response = client.post("/voices/preview", json={"voice_id": "bad_id"})

    assert response.status_code == 502
    data = response.json()
    assert data["success"] is False


# --- WebSocket set_voice ---


def test_ws_set_voice_acknowledged(client: TestClient):
    """Sending set_voice returns a voice_set confirmation."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "set_voice", "voice_id": "abc123"}))
        data = ws.receive_json()

        assert data["type"] == "voice_set"
        assert data["voice_id"] == "abc123"


def test_ws_set_voice_used_in_tts(client: TestClient):
    """After set_voice, subsequent messages use the stored voice_id for TTS."""
    mock_agent_result = {
        "content": "I hear you.",
        "emotion": "neutral",
        "events": [],
    }
    mock_tts = MagicMock(return_value=b"audio-bytes")

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", mock_tts),
    ):
        with client.websocket_connect("/ws") as ws:
            # Set voice preference
            ws.send_text(json.dumps({"type": "set_voice", "voice_id": "my_voice"}))
            ws.receive_json()  # consume voice_set ack

            # Send a text message — should use the stored voice
            ws.send_text(json.dumps({"type": "text", "content": "hello"}))
            data = ws.receive_json()

            assert data["type"] == "response"
            assert "audio_base64" in data

            # Verify text_to_speech was called with the stored voice_id
            mock_tts.assert_called_once()
            call_args = mock_tts.call_args
            assert call_args[0][1] == "my_voice" or call_args[1].get("voice_id") == "my_voice"


def test_ws_per_message_voice_overrides_stored(client: TestClient):
    """A voice_id in the message overrides the stored connection preference."""
    mock_agent_result = {
        "content": "Got it.",
        "emotion": "calm",
        "events": [],
    }
    mock_tts = MagicMock(return_value=b"audio")

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", mock_tts),
    ):
        with client.websocket_connect("/ws") as ws:
            # Set a stored preference
            ws.send_text(json.dumps({"type": "set_voice", "voice_id": "stored_voice"}))
            ws.receive_json()

            # Send message with per-message override
            ws.send_text(json.dumps({"type": "text", "content": "hi", "voice_id": "override_voice"}))
            ws.receive_json()

            # TTS should use the per-message voice_id
            call_args = mock_tts.call_args
            assert call_args[0][1] == "override_voice"


def test_ws_clear_voice_resets_to_default(client: TestClient):
    """Sending set_voice with empty string clears the preference."""
    with client.websocket_connect("/ws") as ws:
        # Set then clear
        ws.send_text(json.dumps({"type": "set_voice", "voice_id": "abc123"}))
        ws.receive_json()

        ws.send_text(json.dumps({"type": "set_voice", "voice_id": ""}))
        data = ws.receive_json()

        assert data["type"] == "voice_set"
        assert data["voice_id"] is None
