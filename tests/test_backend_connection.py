"""Tests for frontend ↔ backend connection contracts.

Verifies that every endpoint the frontend talks to returns the
expected shape, status code, and content-type — with all external
services (Gemini, ElevenLabs) mocked out.
"""

import json
from unittest.mock import patch, AsyncMock, MagicMock

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
_stt_patch = patch(
    "multi_tool_agent.voice_agent.speech_to_text",
    return_value="transcribed text from audio",
)
_tts_patch = patch(
    "multi_tool_agent.voice_agent.text_to_speech",
    return_value=b"fake-audio-bytes",
)

_run_agent_patch = patch(
    "app.services.agent_runner.run_agent",
    new_callable=AsyncMock,
    return_value={
        "content": "I hear you. That sounds really tough.",
        "emotion": "stressed",
        "events": [],
    },
)


_emotion_mock = _emotion_patch.start()
_resource_mock = _resource_patch.start()
_stt_mock = _stt_patch.start()
_tts_mock = _tts_patch.start()
_run_agent_mock = _run_agent_patch.start()

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app  # noqa: E402

client = TestClient(app)


def teardown_module() -> None:
    _emotion_patch.stop()
    _resource_patch.stop()
    _stt_patch.stop()
    _tts_patch.stop()
    _run_agent_patch.stop()


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
        "app.api.routes.speech.text_to_speech",
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


# ---------- Transcribe (POST /transcribe) ----------

import base64


def test_transcribe_returns_200():
    audio_b64 = base64.b64encode(b"fake-audio").decode()
    resp = client.post("/transcribe", json={"audio_base64": audio_b64})
    assert resp.status_code == 200


def test_transcribe_response_shape():
    """Frontend expects { success: true, transcript: '...' }."""
    audio_b64 = base64.b64encode(b"fake-audio").decode()
    data = client.post("/transcribe", json={"audio_base64": audio_b64}).json()
    assert data["success"] is True
    assert "transcript" in data
    assert isinstance(data["transcript"], str)


def test_transcribe_empty_payload_returns_422():
    """Missing audio_base64 should fail validation."""
    resp = client.post("/transcribe", json={})
    assert resp.status_code == 422


def test_transcribe_failure_returns_502():
    """When STT fails, frontend expects a 502 JSON error."""
    with patch(
        "app.api.routes.speech.speech_to_text",
        side_effect=RuntimeError("STT down"),
    ):
        audio_b64 = base64.b64encode(b"fake-audio").decode()
        resp = client.post("/transcribe", json={"audio_base64": audio_b64})
    assert resp.status_code == 502
    data = resp.json()
    assert data["success"] is False
    assert "error" in data


# ---------- WebSocket audio messages ----------

def test_ws_audio_message_returns_transcript_and_response():
    """Frontend sends { type: 'audio', content: '<base64>' },
    expects back a transcript message then a response message."""
    audio_b64 = base64.b64encode(b"fake-audio").decode()
    with client.websocket_connect("/ws") as ws:
        ws.send_text(json.dumps({"type": "audio", "content": audio_b64}))
        transcript_msg = ws.receive_json()
        response_msg = ws.receive_json()

        assert transcript_msg["type"] == "transcript"
        assert isinstance(transcript_msg["content"], str)

        assert response_msg["type"] == "response"
        assert "content" in response_msg
        assert "emotion" in response_msg
