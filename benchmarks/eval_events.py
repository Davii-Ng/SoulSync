"""Scores calendar-event detection in backend/app/services/agent_runner.py.

Usage:
    python benchmarks/eval_events.py          # offline: regex gate precision/recall
    python benchmarks/eval_events.py --live   # also score Gemini field extraction (spends ~N Gemini calls)

The regex gate (_CALENDAR_PATTERN) decides whether the extra Gemini call runs.
Low precision there wastes calls; low recall misses events.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

DATA = Path(__file__).parent / "datasets" / "events.jsonl"
RESULTS = Path(__file__).parent / "results"


def load() -> list[dict]:
    with open(DATA, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def gate_metrics(rows: list[dict], pattern) -> dict:
    tp = fp = fn = tn = 0
    false_positives, false_negatives = [], []
    for r in rows:
        hit = bool(pattern.search(r["text"]))
        if hit and r["has_event"]:
            tp += 1
        elif hit and not r["has_event"]:
            fp += 1
            false_positives.append(r["text"])
        elif not hit and r["has_event"]:
            fn += 1
            false_negatives.append(r["text"])
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": len(rows), "precision": round(precision, 3), "recall": round(recall, 3),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "false_positives": false_positives, "false_negatives": false_negatives,
    }


async def live_metrics(rows: list[dict], extract) -> dict:
    """Runs the real extractor on rows that have an event; checks title and time."""
    positives = [r for r in rows if r["has_event"]]
    title_ok = time_ok = found = 0
    failures = []
    for r in positives:
        data = await extract(r["text"])
        if not data:
            failures.append({"text": r["text"], "got": None})
            continue
        found += 1
        t_ok = r["title_contains"].lower() in (data.get("title", "").lower())
        tm_ok = (not r["time"]) or data.get("time", "") == r["time"]
        title_ok += t_ok
        time_ok += tm_ok
        if not (t_ok and tm_ok):
            failures.append({"text": r["text"], "got": data})
    n = len(positives)
    return {
        "n": n, "extracted_rate": round(found / n, 3),
        "title_accuracy": round(title_ok / n, 3), "time_accuracy": round(time_ok / n, 3),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    rows = load()
    os.environ.setdefault("GOOGLE_API_KEY", "offline")  # import needs a key; --live needs a real one
    os.environ.setdefault("ELEVENLABS_API_KEY", "offline")
    from app.services import agent_runner
    pattern, extract = agent_runner._CALENDAR_PATTERN, agent_runner._extract_event

    result = {"regex_gate": gate_metrics(rows, pattern)}
    if args.live:
        result["live_extraction"] = asyncio.run(live_metrics(rows, extract))

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "events.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    g = result["regex_gate"]
    print(f"regex gate  n={g['n']}  precision={g['precision']:.0%}  recall={g['recall']:.0%}  (tp={g['tp']} fp={g['fp']} fn={g['fn']} tn={g['tn']})")
    print(f"  false positives: {g['false_positives']}")
    print(f"  false negatives: {g['false_negatives']}")
    if "live_extraction" in result:
        x = result["live_extraction"]
        print(f"live extract n={x['n']}  extracted={x['extracted_rate']:.0%}  title={x['title_accuracy']:.0%}  time={x['time_accuracy']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
