"""Microbenchmark: analyze_emotion latency per call (pure Python, no LLM).

Usage: python benchmarks/bench_engine.py [--rounds 20]
Writes benchmarks/results/engine.json.
"""

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from multi_tool_agent.core_companion import analyze_emotion  # noqa: E402

DATA = Path(__file__).parent / "datasets" / "emotion_labeled.jsonl"
RESULTS = Path(__file__).parent / "results"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=20)
    args = parser.parse_args()

    with open(DATA, encoding="utf-8") as f:
        texts = [json.loads(line)["text"] for line in f if line.strip()]

    for t in texts:  # warm up regex caches
        analyze_emotion(t)

    per_call_us: list[float] = []
    for _ in range(args.rounds):
        for t in texts:
            start = time.perf_counter_ns()
            analyze_emotion(t)
            per_call_us.append((time.perf_counter_ns() - start) / 1000)

    per_call_us.sort()
    result = {
        "calls": len(per_call_us),
        "mean_us": round(statistics.fmean(per_call_us), 1),
        "p50_us": round(per_call_us[len(per_call_us) // 2], 1),
        "p95_us": round(per_call_us[int(len(per_call_us) * 0.95)], 1),
        "p99_us": round(per_call_us[int(len(per_call_us) * 0.99)], 1),
        "calls_per_second": round(1_000_000 / statistics.fmean(per_call_us)),
    }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "engine.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"analyze_emotion: {result['calls']} calls  p50={result['p50_us']}us  p95={result['p95_us']}us  "
          f"p99={result['p99_us']}us  ~{result['calls_per_second']:,}/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
