"""Runs the real SoulSync backend with Gemini and ElevenLabs replaced by fixed-delay stubs.

Used by bench_load.py to measure the backend's own overhead (WebSocket handling,
emotion analysis, thread-pool use, JSON/base64 work) without vendor rate limits.

    python benchmarks/_stub_server.py --port 8123 [--llm-ms 300] [--tts-ms 800]

The stubs block a worker thread for the delay, like the real synchronous SDK calls do
(both are invoked through asyncio.to_thread), so thread-pool saturation is represented.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("GOOGLE_API_KEY", "stub")
os.environ.setdefault("ELEVENLABS_API_KEY", "stub")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--llm-ms", type=float, default=300)
    parser.add_argument("--tts-ms", type=float, default=800)
    args = parser.parse_args()

    import uvicorn
    from app.api.routes import ws as ws_routes
    from app.services import agent_runner

    audio = b"\x00" * 20_000  # ~ size of a short mp3 reply

    def fake_generate_content(*, model, contents, config=None, **_):
        time.sleep(args.llm_ms / 1000)
        wants_json = getattr(config, "response_mime_type", None) == "application/json"
        text = '{"title": ""}' if wants_json else "I hear you. That sounds like a lot, what's weighing on you most?"
        return SimpleNamespace(
            text=text,
            usage_metadata=SimpleNamespace(prompt_token_count=300, candidates_token_count=40),
        )

    def fake_tts(text, voice_id=None):
        time.sleep(args.tts_ms / 1000)
        return audio

    agent_runner._gemini.models.generate_content = fake_generate_content  # type: ignore[method-assign]
    ws_routes.text_to_speech = fake_tts

    from main import app
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="error")


if __name__ == "__main__":
    main()
