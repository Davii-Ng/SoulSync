# SoulSync benchmark results

Generated 2026-09-30 from commit `5a22b61` (plus uncommitted changes if any). Every number below comes from a script in `benchmarks/`; raw output is in `benchmarks/results/`.

## Emotion and crisis detection (`eval_emotion.py`)

Offline, deterministic. Engine: `multi_tool_agent/core_companion.py::analyze_emotion` (keyword tiers + negation + crisis rules).

| Metric | Result | Sample |
| --- | --- | --- |
| Crisis recall | **100.0%** (was 90.0% before fixing inflected phrases such as "killing myself") | 30 hand-written crisis messages |
| Crisis false-positive rate | 2.8% overall; 4/33 on hard negatives ("overdose of caffeine", "paper on self-harm statistics") | 144 non-crisis messages |
| Emotion accuracy (7 labels) | 94.6%, macro-F1 0.955 | 111 hand-labeled messages |
| Negation subset accuracy | 61.5% with handling vs 23.1% without | negation messages |
| Mixed emotions | primary 100.0%, secondary 100.0% | 10 messages |
| **External check**, `dair-ai/emotion` (joy/sadness/anger/fear) | accuracy 16.8%, macro-F1 0.271; predicts neutral on 69.8% | 500 tweets |

**Read this carefully.** The in-house set was written by the engine's authors, so its accuracy is optimistic. The external result is the honest generalization number: the keyword engine only recognizes phrases it knows. In the product, Gemini writes the reply and picks up what the keywords miss; the engine's real job is the instant, free, auditable crisis check, which is why recall is the headline metric.

## Calendar intent (`eval_events.py`)

Regex gate that decides whether to spend a second Gemini call: precision 76.9%, recall 100.0% on 40 messages (6 false positives, mostly bare weekday/"tomorrow" mentions). Live field-extraction accuracy: not run (needs Gemini quota; `--live`).

## Emotion engine speed (`bench_engine.py`)

`analyze_emotion`: p50 16.7 µs, p95 21.2 µs, p99 23.6 µs (~59,406 calls/s, single thread, 2220 calls). No network, no LLM cost.

## Concurrency (`bench_load.py`, Gemini and ElevenLabs stubbed)

Stubs: 300 ms LLM, 800 ms TTS, so the floor is 0.30 s to text. Machine: Intel64 Family 6 Model 198 Stepping 2, GenuineIntel, Python 3.13.11.

| Concurrent sessions | Messages | Errors | Text p50 | Text p95 | Throughput | Server RSS |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 50 | 0 | 0.303 s | 0.312 s | 9.0 msg/s | 143.2 MB |
| 50 | 250 | 0 | 1.199 s | 1.402 s | 16.9 msg/s | 157.7 MB |
| 100 | 500 | 0 | 2.601 s | 3.003 s | 16.8 msg/s | 192.1 MB |
| 200 | 1000 | 0 | 5.408 s | 6.303 s | 17.0 msg/s | 260.3 MB |

Zero errors up to the largest level tested. Latency stays at the floor to about 10 sessions, then grows linearly while throughput plateaus near 17 msg/s. Likely cause (consistent with 24 threads / ~1.1 s per message ≈ 22 msg/s ceiling): the Gemini and ElevenLabs SDK calls are synchronous and run through `asyncio.to_thread` on Python's default pool (`min(32, cpu+4)` = 24 threads here), so each in-flight message holds a thread for its whole provider call. Switching to the SDKs' async clients, or a larger pool, is the obvious next optimization. These numbers measure SoulSync's overhead only, not vendor rate limits.

## End-to-end latency (`bench_latency.py`, real Gemini)

Not run yet. The Gemini key used so far is on the free tier (20 requests/day for this model), which is too small for a before/after comparison. See `benchmarks/README.md` for how to run it.

## Tests and coverage

| Suite | Tests | Coverage |
| --- | ---: | ---: |
| Backend (`backend/tests`) | 25 | 78% of `backend/app` |
| Agents + emotion engine (`tests/`) | 104 | 69% of `multi_tool_agent` (98% for `core_companion.py`) |
| Frontend (`vitest`) | 13 | not measured |

CI (`.github/workflows/main.yml`) runs all three suites plus a gate that fails the build if crisis recall drops below 100%.

## Frontend

Production bundle: 268.77 kB JS (83.05 kB gzip), 6.39 kB CSS gzip.

- Lighthouse 13.5.0 (mobile) on the live Vercel site: performance 57, accessibility 91, best practices 96, SEO 91; FCP 8.6 s.
- Lighthouse 13.5.0 (desktop) on the live Vercel site: performance 100, accessibility 86, best practices 96, SEO 91; FCP 0.6 s.
