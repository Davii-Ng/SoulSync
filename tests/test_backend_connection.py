"""Tests for frontend ↔ backend connection contracts.

Verifies that every endpoint the frontend talks to returns the
expected shape, status code, and content-type — with all external
services (Gemini, ElevenLabs) mocked out.
"""

import json
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

# Patch external service calls before importing the app
_emotion_patch = patch(
    "multi_tool_agent.core_companion.analyze_emotion",
    return_value={"emotion": "stressed"},
)
_resource_patch = patch(
    "multi_tool_agent.core_companion.suggest_resource",
    return_value={"suggestion": "Try deep breathing for 5 minutes."},
)
_tts_patch = patch(
    "multi_tool_agent.voice_agent.text_to_speech",
    new_callable=AsyncMock,
    return_value=b"fake-audio-bytes",
)

_emotion_patch.start()
_resource_patch.start()
_tts_patch.start()

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app  # noqa: E402

client = TestClient(app)


# ---------- Health (GET /) ----------

def test_health_returns_200():
    resp = client.get("/")
    assert resp.status_code == 200


def test_health_response_shape():
    """Frontend expects { success, data: { status, service, version } }."""
    data = client.get("/").json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["service"] == "SoulSync"
    assert "version" in data["data"]
    assert "request_id" in data


# ---------- Chat (POST /chat) ----------

def test_chat_returns_200():
    resp = client.post("/chat", json={"message": "I feel overwhelmed"})
    assert resp.status_code == 200


def test_chat_response_shape():
    """Frontend expects { success, data: { content, emotion } }."""
    data = client.post("/chat", json={"message": "I feel overwhelmed"}).json()
    assert data["success"] is True
    assert "content" in data["data"]
    assert "emotion" in data["data"]
    assert isinstance(data["data"]["content"], str)
    assert isinstance(data["data"]["emotion"], str)


def test_chat_empty_message_returns_422():
    """Pydantic should reject missing 'message' field."""
    resp = client.post("/chat", json={})
    assert resp.status_code == 422


def test_chat_with_context():
    """Optional context field should be accepted."""
    resp = client.post(
        "/chat",
        json={
            "message": "hello",
            "context": [{"role": "user", "content": "hi"}],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


# ---------- Speech (POST /speech) ----------

def test_speech_returns_audio_bytes():
    resp = client.post("/speech", json={"text": "Hello world"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/mpeg"
    assert resp.content == b"fake-audio-bytes"


def test_speech_empty_text_returns_422():
    """Pydantic should reject missing 'text' field."""
    resp = client.post("/speech", json={})
    assert resp.status_code == 422


def test_speech_with_voice_id():
    """Optional voice_id should be accepted."""
    resp = client.post("/speech", json={"text": "hi", "voice_id": "custom123"})
    assert resp.status_code == 200


def test_speech_failure_returns_502():
    """When TTS fails, frontend expects a 502 JSON error."""
    with patch(
        "app.api.routes.speech.voice_agent.text_to_speech",
        new_callable=AsyncMock,
        side_effect=RuntimeError("TTS down"),
    ):
        resp = client.post("/speech", json={"text": "test"})
    assert resp.status_code == 502
    data = resp.json()
    assert data["success"] is False
    assert "error" in data


# ---------- WebSocket (WS /ws) ----------

def test_ws_connects():
    """Frontend should be able to open a WebSocket."""
    with client.websocket_connect("/ws") as ws:
        assert ws is not None


def test_ws_text_message_response_shape():
    """Frontend sends { type: 'text', content: '...' },
    expects back { type: 'response', content, emotion }."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "text", "content": "I'm stressed"}))
        resp = ws.receive_json()

        assert resp["type"] == "response"
        assert "content" in resp
        assert "emotion" in resp
        assert isinstance(resp["content"], str)
        assert isinstance(resp["emotion"], str)


def test_ws_response_includes_audio():
    """When TTS succeeds, response should include audio_base64."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "text", "content": "help me"}))
        resp = ws.receive_json()

        assert "audio_base64" in resp
        assert isinstance(resp["audio_base64"], str)
        assert len(resp["audio_base64"]) > 0


def test_ws_empty_content_returns_error():
    """Empty content should return an error message."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "text", "content": ""}))
        resp = ws.receive_json()
        assert resp["type"] == "error"


def test_ws_unsupported_type_returns_error():
    """Unknown message type with no content should return error."""
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "binary", "content": ""}))
        resp = ws.receive_json()
        assert resp["type"] == "error"


def test_ws_multiple_messages():
    """Frontend can send multiple messages on the same connection."""
    with client.websocket_connect("/ws") as ws:
        for text in ["first message", "second message"]:
            ws.send_text(json.dumps({"type": "text", "content": text}))
            resp = ws.receive_json()
            assert resp["type"] == "response"
            assert resp["content"]  # non-empty
