"""Tests for multi_tool_agent.voice_agent"""

from unittest.mock import patch, MagicMock
import pytest

import multi_tool_agent.voice_agent as va


# --- speak_response ---

def test_speak_response_no_client():
    """Returns error dict when ElevenLabs client is None."""
    with patch.object(va, "_client", None):
        result = va.speak_response("hello")
    assert result["status"] == "error"
    assert "ELEVENLABS_API_KEY" in result["message"]


def test_speak_response_success():
    """Returns success with audio byte count on valid TTS call."""
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = [b"fake", b"audio"]

    with patch.object(va, "_client", mock_client):
        result = va.speak_response("hello world")

    assert result["status"] == "success"
    assert result["audio_bytes"] == 9  # len(b"fakeaudio")
    mock_client.text_to_speech.convert.assert_called_once_with(
        voice_id=va._voice_id,
        text="hello world",
        model_id=va._model_id,
        output_format="mp3_44100_128",
    )


def test_speak_response_tts_exception():
    """Returns error dict when ElevenLabs raises."""
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.side_effect = RuntimeError("quota exceeded")

    with patch.object(va, "_client", mock_client):
        result = va.speak_response("hi")

    assert result["status"] == "error"
    assert "quota exceeded" in result["message"]


# --- text_to_speech ---

def test_text_to_speech_no_client():
    """Raises RuntimeError when client is None."""
    with patch.object(va, "_client", None):
        with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
            va.text_to_speech("hello")


def test_text_to_speech_returns_bytes():
    """Returns concatenated audio bytes from TTS."""
    mock_client = MagicMock()
    mock_client.text_to_speech.convert.return_value = [b"mp3", b"data"]

    with patch.object(va, "_client", mock_client):
        result = va.text_to_speech("test", voice_id="custom_id")

    assert result == b"mp3data"
    mock_client.text_to_speech.convert.assert_called_once_with(
        voice_id="custom_id",
        text="test",
        model_id=va._model_id,
        output_format="mp3_44100_128",
    )


# --- get_available_voices ---

@pytest.mark.asyncio
async def test_get_available_voices_no_client():
    """Raises RuntimeError when client is None."""
    with patch.object(va, "_client", None):
        with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
            await va.get_available_voices()


@pytest.mark.asyncio
async def test_get_available_voices_returns_list():
    """Returns list of voice dicts."""
    mock_voice = MagicMock()
    mock_voice.voice_id = "v1"
    mock_voice.name = "Rachel"
    mock_voice.labels = {"gender": "female"}

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.voices = [mock_voice]
    mock_client.voices.get_all.return_value = mock_response

    with patch.object(va, "_client", mock_client):
        voices = await va.get_available_voices()

    assert voices == [{"voice_id": "v1", "name": "Rachel", "gender": "female"}]


# --- speech_to_text ---

def test_speech_to_text_no_client():
    """Raises RuntimeError when client is None."""
    with patch.object(va, "_client", None):
        with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
            va.speech_to_text(b"audio-data")


def test_speech_to_text_returns_transcript():
    """Returns transcript string from STT response."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello, how are you?"
    mock_client.speech_to_text.convert.return_value = mock_response

    with patch.object(va, "_client", mock_client):
        result = va.speech_to_text(b"audio-data")

    assert result == "Hello, how are you?"
    mock_client.speech_to_text.convert.assert_called_once_with(
        model_id="scribe_v1",
        file=b"audio-data",
        language_code=None,
    )


def test_speech_to_text_with_language_code():
    """Passes language_code to ElevenLabs when provided."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hola"
    mock_client.speech_to_text.convert.return_value = mock_response

    with patch.object(va, "_client", mock_client):
        result = va.speech_to_text(b"audio-data", language_code="es")

    assert result == "Hola"
    mock_client.speech_to_text.convert.assert_called_once_with(
        model_id="scribe_v1",
        file=b"audio-data",
        language_code="es",
    )


# --- Agent configuration ---

def test_voice_agent_config():
    """voice_agent Agent is wired correctly."""
    assert va.voice_agent.name == "voice_agent"
    assert va.speak_response in va.voice_agent.tools
