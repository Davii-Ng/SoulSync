"""End-to-end WebSocket latency benchmark against a SoulSync checkout.

Starts that checkout's backend as a subprocess, plays scripted conversations over a
real WebSocket, and records client-side timings:

    time_to_text   user sends message -> reply text arrives (text_ready, or legacy 'response')
    time_to_audio  user sends message -> audio arrives (audio_ready / audio_error / legacy 'response')

Usage:
    python benchmarks/bench_latency.py --label current
    python benchmarks/bench_latency.py --label adk-baseline --repo ../soulsync-baseline --patch-model
    python benchmarks/bench_latency.py --label current --no-tts      # skip ElevenLabs spend (time_to_text unaffected)

Spends real Gemini (and, without --no-tts, ElevenLabs) quota: one call per message, plus
one extra Gemini call on calendar messages in the current pipeline.
Writes benchmarks/results/latency_<label>.json.
"""

import argparse
import asyncio
import json
import os
import re
import socket
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets
from dotenv import dotenv_values

HERE = Path(__file__).resolve().parent
MAIN_REPO = HERE.parent
RESULTS = HERE / "results"
CONVERSATIONS = HERE / "datasets" / "latency_conversations.json"
MODEL = "gemini-3-flash-preview"
TIMEOUT_S = 45.0  # per message; provider 503 retries can stall far longer


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def patch_model(repo: Path) -> list[str]:
    """Point every hardcoded Gemini model at MODEL (old commits used deprecated ids)."""
    changed = []
    targets = list((repo / "multi_tool_agent").glob("*.py")) + list((repo / "backend").rglob("*.py"))
    for path in targets:
        text = path.read_text(encoding="utf-8")
        new = re.sub(r'(model\s*=\s*)"gemini-[^"]+"', rf'\1"{MODEL}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(repo)))
    return changed


def start_server(repo: Path, port: int, no_tts: bool) -> subprocess.Popen:
    env = os.environ.copy()
    for key, value in dotenv_values(MAIN_REPO / "backend" / ".env").items():
        if value:
            env.setdefault(key.strip(), value)
    if no_tts:
        env["ELEVENLABS_API_KEY"] = "benchmark-disabled-key"
    env["PYTHONPATH"] = str(repo)
    env["PYTHONUTF8"] = "1"
    log = open(HERE / "results" / f"server_{port}.log", "w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(port), "--log-level", "warning"],
        cwd=repo / "backend", env=env, stdout=log, stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 90
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"server exited early, see results/server_{port}.log")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1)
            return proc
        except Exception:
            time.sleep(0.5)
    proc.kill()
    raise RuntimeError("server did not become healthy in 90s")


async def send_and_time(ws, text: str, timeout: float = 90.0) -> dict:
    """Sends one message and returns timing for text and audio arrival (seconds)."""
    started = time.perf_counter()
    await ws.send(json.dumps({"type": "text", "content": text}))
    t_text = t_audio = None
    audio_ok = None
    reply = ""
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        now = time.perf_counter() - started
        msg = json.loads(raw)
        kind = msg.get("type")
        if kind == "text_ready":
            t_text, reply = now, msg.get("content", "")
        elif kind in ("audio_ready", "audio_error"):
            t_audio, audio_ok = now, kind == "audio_ready"
            break
        elif kind == "response":  # legacy single-frame protocol: text and audio together
            t_text = t_audio = now
            reply, audio_ok = msg.get("content", ""), bool(msg.get("audio_base64"))
            break
        elif kind == "error":
            return {"error": msg.get("content", "error"), "t_total": now}
    return {"time_to_text": t_text, "time_to_audio": t_audio, "audio_ok": audio_ok, "reply_chars": len(reply)}


async def run_conversations(port: int, conversations: list[list[dict]]) -> list[dict]:
    uri = f"ws://127.0.0.1:{port}/ws"
    records = []
    # Warm-up: imports, client init, first-token cold start. Not recorded.
    try:
        async with websockets.connect(uri, max_size=None) as ws:
            for text in ("Hi there.", "I'm feeling okay today."):
                await send_and_time(ws, text, timeout=TIMEOUT_S)
    except asyncio.TimeoutError:
        print("  warm-up timed out (provider overloaded?), continuing")
    for c_idx, conv in enumerate(conversations):
        async with websockets.connect(uri, max_size=None) as ws:
            for turn, item in enumerate(conv):
                try:
                    result = await send_and_time(ws, item["text"], timeout=TIMEOUT_S)
                except asyncio.TimeoutError:
                    # Late replies would corrupt later timings on this socket: drop the session.
                    records.append({"conversation": c_idx, "turn": turn, "kind": item["kind"],
                                    "error": f"timeout>{TIMEOUT_S:.0f}s"})
                    print(f"  c{c_idx} t{turn} [{item['kind']:8}] TIMEOUT")
                    break
                result.update({"conversation": c_idx, "turn": turn, "kind": item["kind"]})
                records.append(result)
                print(f"  c{c_idx} t{turn} [{item['kind']:8}] "
                      f"text={result.get('time_to_text', float('nan')):.2f}s "
                      f"audio={result.get('time_to_audio') or float('nan'):.2f}s"
                      + (f"  ERROR {result['error']}" if "error" in result else ""))
    return records


def pct(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))]


def summarize(records: list[dict], field: str) -> dict:
    values = [r[field] for r in records if field in r and r[field] is not None]
    if not values:
        return {"n": 0}
    return {
        "n": len(values), "mean_s": round(statistics.fmean(values), 3),
        "p50_s": round(pct(values, 0.5), 3), "p95_s": round(pct(values, 0.95), 3),
        "min_s": round(min(values), 3), "max_s": round(max(values), 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--repo", default=str(MAIN_REPO), help="checkout to benchmark (default: this repo)")
    parser.add_argument("--patch-model", action="store_true", help="rewrite hardcoded Gemini model ids in that checkout")
    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--repeat", type=int, default=1, help="repeat the conversation set N times")
    parser.add_argument("--limit", type=int, default=0,
                        help="keep only the first N messages (spread across conversations) to fit a small API quota")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    RESULTS.mkdir(exist_ok=True)
    patched = patch_model(repo) if args.patch_model else []
    conversations = json.loads(CONVERSATIONS.read_text(encoding="utf-8"))["conversations"] * args.repeat
    if args.limit:
        # Take the same leading turns of every conversation so history depth stays realistic.
        depth = max(1, -(-args.limit // len(conversations)))
        conversations = [c[:depth] for c in conversations]

    port = free_port()
    print(f"[{args.label}] starting backend from {repo} on :{port}")
    proc = start_server(repo, port, args.no_tts)
    try:
        records = asyncio.run(run_conversations(port, conversations))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

    ok = [r for r in records if "error" not in r]
    kinds = sorted({r["kind"] for r in ok})
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
    result = {
        "label": args.label, "commit": sha, "repo": str(repo), "patched_files": patched,
        "tts_enabled": not args.no_tts, "messages": len(records), "errors": len(records) - len(ok),
        "time_to_text": summarize(ok, "time_to_text"),
        "time_to_audio": summarize(ok, "time_to_audio") if not args.no_tts else None,
        "by_kind_time_to_text": {k: summarize([r for r in ok if r["kind"] == k], "time_to_text") for k in kinds},
        "raw": records,
    }
    (RESULTS / f"latency_{args.label}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    t = result["time_to_text"]
    print(f"[{args.label}] n={t['n']} errors={result['errors']}  time_to_text p50={t['p50_s']}s p95={t['p95_s']}s mean={t['mean_s']}s")
    for k, s in result["by_kind_time_to_text"].items():
        print(f"    {k:9} n={s['n']} p50={s['p50_s']}s p95={s['p95_s']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
