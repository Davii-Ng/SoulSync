"""Concurrency benchmark for the backend with Gemini/ElevenLabs stubbed (see _stub_server.py).

Usage:
    python benchmarks/bench_load.py --ladder 10,50,100,200 --messages 5

For each concurrency level, opens that many WebSocket sessions at once; each session
sends `--messages` messages back to back. Reports time_to_text / time_to_audio percentiles,
the overhead over the stubbed floor (llm_ms, llm_ms + tts_ms), error rate, and server RSS.

Numbers measure SoulSync's own overhead on this machine. They say nothing about
Gemini/ElevenLabs rate limits. Writes benchmarks/results/load.json.
"""

import argparse
import asyncio
import json
import platform
import socket
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def pct(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


async def session(uri: str, messages: int, start_gate: asyncio.Event) -> list[dict]:
    out = []
    async with websockets.connect(uri, max_size=None, open_timeout=30) as ws:
        await start_gate.wait()
        for i in range(messages):
            began = time.perf_counter()
            await ws.send(json.dumps({"type": "text", "content": f"I feel stressed about deadline number {i}."}))
            t_text = t_audio = None
            error = None
            while True:
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=60))
                now = time.perf_counter() - began
                if msg["type"] == "text_ready":
                    t_text = now
                elif msg["type"] in ("audio_ready", "audio_error"):
                    t_audio = now
                    break
                elif msg["type"] == "error":
                    error = msg.get("content")
                    break
            out.append({"t_text": t_text, "t_audio": t_audio, "error": error})
    return out


async def run_level(uri: str, concurrency: int, messages: int) -> dict:
    gate = asyncio.Event()
    tasks = [asyncio.create_task(session(uri, messages, gate)) for _ in range(concurrency)]
    await asyncio.sleep(1.0 + concurrency * 0.01)  # let all sockets connect first
    wall_start = time.perf_counter()
    gate.set()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    wall = time.perf_counter() - wall_start

    records = [r for res in results if isinstance(res, list) for r in res]
    failed_sessions = sum(1 for res in results if isinstance(res, Exception))
    errors = sum(1 for r in records if r["error"] or r["t_text"] is None) + failed_sessions * messages
    total = concurrency * messages
    text = [r["t_text"] for r in records if r["t_text"] is not None and not r["error"]]
    audio = [r["t_audio"] for r in records if r["t_audio"] is not None and not r["error"]]
    return {
        "concurrency": concurrency, "messages_total": total, "errors": errors,
        "error_rate": round(errors / total, 4), "wall_s": round(wall, 2),
        "throughput_msg_per_s": round(len(text) / wall, 1),
        "time_to_text_s": {q: round(pct(text, v), 3) for q, v in (("p50", 0.5), ("p95", 0.95), ("p99", 0.99))} if text else None,
        "time_to_audio_s": {q: round(pct(audio, v), 3) for q, v in (("p50", 0.5), ("p95", 0.95), ("p99", 0.99))} if audio else None,
    }


def rss_mb(pid: int) -> float | None:
    try:
        import psutil
        # venv launchers spawn the real interpreter as a child: sum the tree.
        root = psutil.Process(pid)
        procs = [root, *root.children(recursive=True)]
        return round(sum(p.memory_info().rss for p in procs) / 1e6, 1)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ladder", default="10,50,100,200")
    parser.add_argument("--messages", type=int, default=5)
    parser.add_argument("--llm-ms", type=float, default=300)
    parser.add_argument("--tts-ms", type=float, default=800)
    args = parser.parse_args()

    port = free_port()
    proc = subprocess.Popen(
        [sys.executable, str(HERE / "_stub_server.py"), "--port", str(port),
         "--llm-ms", str(args.llm_ms), "--tts-ms", str(args.tts_ms)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    deadline = time.time() + 60
    while True:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            break
        except Exception:
            if proc.poll() is not None or time.time() > deadline:
                proc.kill()
                raise RuntimeError("stub server failed to start")
            time.sleep(0.4)

    uri = f"ws://127.0.0.1:{port}/ws"
    levels = []
    try:
        asyncio.run(run_level(uri, 2, 2))  # warm-up
        for c in (int(x) for x in args.ladder.split(",")):
            level = asyncio.run(run_level(uri, c, args.messages))
            level["server_rss_mb"] = rss_mb(proc.pid)
            levels.append(level)
            t = level["time_to_text_s"] or {}
            print(f"c={c:4}  msgs={level['messages_total']:5}  errors={level['errors']:3}  "
                  f"text p50={t.get('p50')}s p95={t.get('p95')}s p99={t.get('p99')}s  "
                  f"{level['throughput_msg_per_s']} msg/s  rss={level['server_rss_mb']}MB")
    finally:
        proc.terminate()

    result = {
        "stub": {"llm_ms": args.llm_ms, "tts_ms": args.tts_ms,
                 "floor_text_s": args.llm_ms / 1000, "floor_audio_s": (args.llm_ms + args.tts_ms) / 1000},
        "machine": {"python": platform.python_version(), "os": platform.platform(), "processor": platform.processor()},
        "levels": levels,
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "load.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
