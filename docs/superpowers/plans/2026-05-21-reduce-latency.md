# Reduce Agent Latency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cut the perceived response latency in half by sending the AI text reply to the frontend immediately after the agent finishes, then streaming the audio separately — so text appears ~2-4 s sooner instead of waiting for TTS to finish before sending anything. Also fix a bug where the system prompt is sent as a user-role message instead of as a system instruction.

**Architecture:** Split the single WebSocket response into two messages — `text_ready` (sent as soon as the agent responds) and `audio_ready` / `audio_error` (sent when TTS finishes). The frontend handles each message type independently: text triggers display, audio triggers playback. The fast path in `agent_runner.py` is also fixed to pass the system prompt via `GenerateContentConfig.system_instruction` instead of prepending it as a fake user message.

**Tech Stack:** FastAPI WebSocket, `asyncio`, `google-genai` SDK, React, TypeScript

---

## File Map

| Action | File | Change |
|---|---|---|
| Modify | `backend/app/api/routes/ws.py:18-60` | Split `_process_text` into two sends: text first, then audio |
| Modify | `backend/app/services/agent_runner.py:190-197` | Fix system instruction passed as user message |
| Modify | `frontend/src/types/index.ts:22-31` | Add `text_ready`, `audio_ready`, `audio_error` to `WsResponse.type` |
| Modify | `frontend/src/App.tsx:98-154` | Handle two-phase protocol in `handleMessage` |
| Modify | `backend/tests/test_ws.py` | Update tests for new two-phase protocol |

---

### Task 1: Update backend WebSocket to send text immediately, audio separately

**Files:**
- Modify: `backend/app/api/routes/ws.py:18-60`

- [ ] **Step 1: Write failing test for two-phase protocol**

Add to `backend/tests/test_ws.py`:

```python
def test_ws_sends_text_before_audio(client: TestClient):
    """Backend sends text_ready immediately, then audio_ready when TTS finishes."""
    import time

    mock_agent_result = {
        "content": "I hear you.",
        "emotion": "calm",
        "events": [],
    }

    def slow_tts(text, voice_id=None):
        time.sleep(0.05)  # simulate TTS delay
        return b"fake-audio-bytes"

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=slow_tts),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I feel calm today"}))

            first = ws.receive_json()
            assert first["type"] == "text_ready"
            assert first["content"] == "I hear you."
            assert first["emotion"] == "calm"
            assert "audio_base64" not in first

            second = ws.receive_json()
            assert second["type"] == "audio_ready"
            assert "audio_base64" in second


def test_ws_sends_audio_error_when_tts_fails(client: TestClient):
    """When TTS fails, backend sends audio_error after text_ready."""
    mock_agent_result = {
        "content": "Take a breath.",
        "emotion": "stressed",
        "events": [],
    }

    with (
        patch("app.api.routes.ws.run_agent", new=AsyncMock(return_value=mock_agent_result)),
        patch("app.api.routes.ws.text_to_speech", side_effect=Exception("quota exceeded")),
    ):
        with client.websocket_connect("/ws") as ws:
            ws.send_text(json.dumps({"type": "text", "content": "I'm stressed"}))

            first = ws.receive_json()
            assert first["type"] == "text_ready"
            assert first["content"] == "Take a breath."

            second = ws.receive_json()
            assert second["type"] == "audio_error"
            assert "tts_error" in second
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd backend && pytest tests/test_ws.py::test_ws_sends_text_before_audio tests/test_ws.py::test_ws_sends_audio_error_when_tts_fails -v
```

Expected: FAIL — `AssertionError: assert 'response' == 'text_ready'`

- [ ] **Step 3: Rewrite `_process_text` in `backend/app/api/routes/ws.py`**

Replace the entire `_process_text` function (lines 18–60):

```python
async def _process_text(websocket: WebSocket, content: str, voice_id: str | None = None) -> None:
    """Run ADK pipeline, send text immediately, then send audio when TTS finishes."""
    try:
        user_id = str(id(websocket))
        agent_result = await run_agent(content, user_id=user_id)
        reply = (agent_result.get("content") or "").strip()
        emotion = agent_result.get("emotion", "neutral")
        events = agent_result.get("events", [])
        journal_saved = agent_result.get("journal_saved", False)
        if not reply:
            reply = "I'm here with you. Want to share a little more about what's on your mind?"
    except Exception as e:
        logger.error(f"Agent processing failed: {e}")
        await manager.send_json(websocket, {
            "type": "error",
            "content": "Something went wrong processing your message. Please try again.",
        })
        return

    # Phase 1 — send text immediately so the frontend can display it now
    text_response: dict = {
        "type": "text_ready",
        "content": reply,
        "emotion": emotion,
    }
    if events:
        text_response["events"] = events
    if journal_saved:
        text_response["journal_saved"] = True
    await manager.send_json(websocket, text_response)

    # Phase 2 — run TTS and send audio when ready
    try:
        audio_bytes = await asyncio.to_thread(text_to_speech, reply, voice_id)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        await manager.send_json(websocket, {"type": "audio_ready", "audio_base64": audio_b64})
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        tts_error = (
            "Voice unavailable — ElevenLabs quota exceeded."
            if "quota" in str(e).lower()
            else "Voice temporarily unavailable."
        )
        await manager.send_json(websocket, {"type": "audio_error", "tts_error": tts_error})
```

- [ ] **Step 4: Run new tests to verify they pass**

```bash
cd backend && pytest tests/test_ws.py::test_ws_sends_text_before_audio tests/test_ws.py::test_ws_sends_audio_error_when_tts_fails -v
```

Expected: PASS

- [ ] **Step 5: Update old tests that still check for `type == "response"`**

In `backend/tests/test_ws.py`, find tests that assert `data["type"] == "response"`. Each of those tests sends one message and receives one response — they now need to receive two. Update each affected test:

`test_ws_text_message_returns_response`:
```python
def test_ws_text_message_returns_response(client: TestClient):
    """Sending a text message returns text_ready then audio_error (TTS fails gracefully)."""
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
            assert data["type"] == "text_ready"
            assert data["content"] == "Keep smiling!"
            assert data["emotion"] == "happy"
            assert "audio_base64" not in data

            audio_msg = ws.receive_json()
            assert audio_msg["type"] == "audio_error"
```

`test_ws_text_message_with_audio`:
```python
def test_ws_text_message_with_audio(client: TestClient):
    """When TTS succeeds, audio_ready message includes audio_base64."""
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

            text_msg = ws.receive_json()
            assert text_msg["type"] == "text_ready"
            assert text_msg["emotion"] == "calm"

            audio_msg = ws.receive_json()
            assert audio_msg["type"] == "audio_ready"
            assert "audio_base64" in audio_msg
```

`test_ws_multiple_messages`:
```python
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
                text_msg = ws.receive_json()
                assert text_msg["type"] == "text_ready"
                audio_msg = ws.receive_json()
                assert audio_msg["type"] == "audio_error"
```

`test_ws_text_message_includes_events_when_returned`:
```python
def test_ws_text_message_includes_events_when_returned(client: TestClient):
    """Events are included in the text_ready message."""
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
            assert data["type"] == "text_ready"
            assert "events" in data
            assert len(data["events"]) == 1
            assert data["events"][0]["title"] == "Therapy check-in"

            ws.receive_json()  # consume audio_error
```

- [ ] **Step 6: Run the full test suite to confirm all pass**

```bash
cd backend && pytest tests/test_ws.py -v
```

Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/api/routes/ws.py backend/tests/test_ws.py
git commit -m "perf: send text_ready immediately, audio_ready after TTS — cuts perceived latency"
```

---

### Task 2: Fix system prompt passed as fake user message in fast path

**Files:**
- Modify: `backend/app/services/agent_runner.py:190-197`

Context: `_run_fast` currently prepends `_COMPANION_SYSTEM` as a `"role": "user"` message in the contents list. This wastes tokens on every request and confuses the model. The correct approach is to pass it as `system_instruction` via `GenerateContentConfig`.

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_agent_runner.py`:

```python
"""Tests for agent_runner fast path."""

import sys
from unittest.mock import MagicMock, patch, AsyncMock

# Stub modules that need API keys before importing agent_runner
for mod in ["multi_tool_agent", "multi_tool_agent.core_companion", "multi_tool_agent.voice_agent"]:
    sys.modules.setdefault(mod, MagicMock())

import os
os.environ.setdefault("GOOGLE_API_KEY", "test-key")
os.environ.setdefault("ELEVENLABS_API_KEY", "test-key")

import pytest


@pytest.mark.asyncio
async def test_fast_path_passes_system_as_instruction_not_user_message():
    """_run_fast must pass system prompt as system_instruction, not as a user-role message."""
    from app.services.agent_runner import _run_fast

    captured_config = {}

    def fake_generate(model, contents, config=None):
        captured_config["config"] = config
        captured_config["contents"] = contents
        result = MagicMock()
        result.text = "I hear you."
        return result

    with (
        patch("app.services.agent_runner._gemini") as mock_gemini,
        patch(
            "app.services.agent_runner.analyze_emotion",
            return_value={"emotion": "neutral", "severity": "low", "secondary_emotion": "none"},
        ),
        patch(
            "app.services.agent_runner.suggest_resource",
            return_value={"suggestion": "breathe", "follow_up": "how are you?"},
        ),
    ):
        mock_gemini.models.generate_content.side_effect = fake_generate
        result = await _run_fast("I feel okay", user_id="test_user")

    assert result["content"] == "I hear you."
    # System prompt must be in config, not in the contents list
    cfg = captured_config.get("config")
    assert cfg is not None, "config must be passed to generate_content"
    assert cfg.system_instruction is not None, "system_instruction must be set"
    for msg in captured_config.get("contents", []):
        parts = msg.get("parts", [])
        for part in parts:
            text = part.get("text", "")
            assert "SoulSync" not in text or "said:" in text, (
                "System prompt must not appear in user-role contents"
            )
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd backend && pytest tests/test_agent_runner.py -v
```

Expected: FAIL — `AssertionError: System prompt must not appear in user-role contents`

- [ ] **Step 3: Fix `_run_fast` in `backend/app/services/agent_runner.py`**

Find the `_run_fast` function. Replace these lines (approximately lines 185–197):

```python
# Before
    contents = [{"role": "user", "parts": [{"text": _COMPANION_SYSTEM}]}] + history

    response = await asyncio.to_thread(
        _gemini.models.generate_content,
        model="gemini-3-flash-preview",
        contents=contents,
    )
```

```python
# After
    from google.genai import types as _gtypes

    _config = _gtypes.GenerateContentConfig(system_instruction=_COMPANION_SYSTEM)

    response = await asyncio.to_thread(
        _gemini.models.generate_content,
        model="gemini-3-flash-preview",
        contents=history,
        config=_config,
    )
```

- [ ] **Step 4: Run test to confirm it passes**

```bash
cd backend && pytest tests/test_agent_runner.py -v
```

Expected: PASS

- [ ] **Step 5: Run full backend test suite**

```bash
cd backend && pytest -v
```

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/agent_runner.py backend/tests/test_agent_runner.py
git commit -m "fix: pass system prompt as system_instruction instead of user-role message in fast path"
```

---

### Task 3: Update frontend to handle two-phase WebSocket protocol

**Files:**
- Modify: `frontend/src/types/index.ts:22-31`
- Modify: `frontend/src/App.tsx:98-154`

- [ ] **Step 1: Extend `WsResponse` type in `frontend/src/types/index.ts`**

Replace lines 22–31:

```typescript
// Before
export interface WsResponse {
  type?: 'response' | 'error' | 'transcript' | 'voice_set'
  content?: string
  emotion?: Emotion
  audio_base64?: string
  tts_error?: string
  events?: SavedEvent[]
  voice_id?: string
  journal_saved?: boolean
}
```

```typescript
// After
export interface WsResponse {
  type?: 'response' | 'text_ready' | 'audio_ready' | 'audio_error' | 'error' | 'transcript' | 'voice_set'
  content?: string
  emotion?: Emotion
  audio_base64?: string
  tts_error?: string
  events?: SavedEvent[]
  voice_id?: string
  journal_saved?: boolean
}
```

- [ ] **Step 2: Update `handleMessage` in `frontend/src/App.tsx`**

The current `handleMessage` (lines 98–154) handles a single `response` message that contains both text and audio. Replace it with a handler that understands `text_ready`, `audio_ready`, and `audio_error`:

```tsx
const handleMessage = (event: MessageEvent) => {
  const data = JSON.parse(event.data) as WsResponse

  if (data.type === 'error') {
    const errMsg: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: data.content || 'Something went wrong.',
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, errMsg])
    setOrbState('idle')
    return
  }

  // Phase 1: text arrives — display immediately, keep thinking state for audio
  if (data.type === 'text_ready' && data.content) {
    const aiMsg: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: data.content,
      timestamp: Date.now(),
      emotion: data.emotion,
    }
    setMessages((prev) => [...prev, aiMsg])
    if (data.emotion) setEmotion(data.emotion)
    if (data.events && data.events.length > 0) {
      setSavedEvents((prev) => mergeEvents(prev, data.events ?? []))
    }
    if (data.journal_saved) snapshotJournal()
    // Stay in 'thinking' state — audio is still being generated
    setOrbState('thinking')
    return
  }

  // Phase 2a: audio arrives — play it
  if (data.type === 'audio_ready' && data.audio_base64) {
    setOrbState('speaking')
    const audio = new Audio(`data:audio/mpeg;base64,${data.audio_base64}`)
    audio.onended = () => setOrbState('idle')
    audio.play().catch(() => setOrbState('idle'))
    return
  }

  // Phase 2b: TTS failed — show note and go idle
  if (data.type === 'audio_error') {
    if (data.tts_error) {
      const note: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: data.tts_error,
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, note])
    }
    setOrbState('idle')
    return
  }

  // Legacy fallback: handle old 'response' type (if backend ever reverts)
  if (data.type === 'response' && data.content) {
    const aiMsg: Message = {
      id: Date.now().toString(),
      role: 'assistant',
      content: data.content,
      timestamp: Date.now(),
      emotion: data.emotion,
      audio_base64: data.audio_base64,
    }
    setMessages((prev) => [...prev, aiMsg])
    if (data.emotion) setEmotion(data.emotion)
    if (data.events && data.events.length > 0) {
      setSavedEvents((prev) => mergeEvents(prev, data.events ?? []))
    }
    if (data.journal_saved) snapshotJournal()
    if (data.tts_error) {
      const note: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content: data.tts_error,
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, note])
    }
    if (data.audio_base64) {
      setOrbState('speaking')
      const audio = new Audio(`data:audio/mpeg;base64,${data.audio_base64}`)
      audio.onended = () => setOrbState('idle')
      audio.play().catch(() => setOrbState('idle'))
    } else {
      setOrbState('idle')
    }
  }
}
```

- [ ] **Step 3: Verify TypeScript compiles**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 4: Manual end-to-end test**

Start both backend and frontend:
```bash
# Terminal 1
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
cd frontend && npm run dev
```

Open `http://localhost:5173`, send a message. Verify:
1. AI text response appears in the chat **before** audio starts playing (text should appear ~1-2 s after send)
2. A moment later, audio plays automatically
3. Orb transitions: `thinking` → text appears → stays `thinking` → audio → `speaking` → `idle`
4. If ElevenLabs is unavailable, text still appears and orb returns to `idle`

- [ ] **Step 5: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/App.tsx
git commit -m "perf: handle two-phase text_ready/audio_ready WebSocket protocol in frontend"
```

---

## Self-Review

**Spec coverage:**
- ✅ Text sent immediately after agent finishes → Task 1
- ✅ Audio sent separately after TTS → Task 1
- ✅ System prompt bug fixed → Task 2
- ✅ Frontend displays text without waiting for audio → Task 3
- ✅ All existing tests updated → Task 1 Step 5–6

**Placeholder scan:** None found — all code blocks are complete.

**Type consistency:**
- `WsResponse.type` in `types/index.ts` is extended, not replaced — legacy `'response'` kept as fallback so nothing breaks if backend is out of sync.
- `text_ready`, `audio_ready`, `audio_error` used consistently in `ws.py` (send) and `App.tsx` (receive).
- `_gtypes.GenerateContentConfig` is the correct import path for `google-genai` SDK.
