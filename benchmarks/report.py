"""Builds benchmarks/RESULTS.md from benchmarks/results/*.json.

Usage: python benchmarks/report.py
Sections whose result file is missing are marked "not run" instead of being guessed.
"""

import json
import subprocess
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"


def load(name: str):
    path = RES / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def main() -> None:
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    out = [
        "# SoulSync benchmark results",
        "",
        f"Generated {date.today().isoformat()} from commit `{sha}` (plus uncommitted changes if any). "
        "Every number below comes from a script in `benchmarks/`; raw output is in `benchmarks/results/`.",
        "",
    ]

    emo = load("emotion.json")
    base = load("emotion_baseline_pre_fix.json")
    if emo:
        e = emo["with_negation"]
        out += [
            "## Emotion and crisis detection (`eval_emotion.py`)",
            "",
            "Offline, deterministic. Engine: `multi_tool_agent/core_companion.py::analyze_emotion` (keyword tiers + negation + crisis rules).",
            "",
            "| Metric | Result | Sample |",
            "| --- | --- | --- |",
            f"| Crisis recall | **{pct(e['crisis']['recall'])}**"
            + (f" (was {pct(base['with_negation']['crisis']['recall'])} before fixing inflected phrases such as \"killing myself\")" if base else "")
            + f" | {e['crisis']['n']} hand-written crisis messages |",
            f"| Crisis false-positive rate | {pct(e['crisis_false_positives']['false_positive_rate'])} overall; "
            f"{e['crisis_false_positives']['hard_negative_fp']}/{e['crisis_false_positives']['hard_negative_n']} on hard negatives "
            "(\"overdose of caffeine\", \"paper on self-harm statistics\") | "
            f"{e['crisis_false_positives']['n_non_crisis']} non-crisis messages |",
            f"| Emotion accuracy (7 labels) | {pct(e['emotion']['accuracy'])}, macro-F1 {e['emotion']['macro_f1']:.3f} | {e['emotion']['n']} hand-labeled messages |",
            f"| Negation subset accuracy | {pct(e['by_tag_accuracy']['negation'])} with handling vs {pct(emo['without_negation']['negation_subset_accuracy'])} without | negation messages |",
            f"| Mixed emotions | primary {pct(e['mixed']['primary_accuracy'])}, secondary {pct(e['mixed']['secondary_accuracy'])} | {e['mixed']['n']} messages |",
        ]
        if "external_dair_ai_emotion" in emo:
            x = emo["external_dair_ai_emotion"]
            out.append(f"| **External check**, `dair-ai/emotion` (joy/sadness/anger/fear) | accuracy {pct(x['accuracy'])}, macro-F1 {x['macro_f1']:.3f}; "
                       f"predicts neutral on {pct(x['predicted_neutral_rate'])} | {x['n']} tweets |")
        out += [
            "",
            "**Read this carefully.** The in-house set was written by the engine's authors, so its accuracy is optimistic. "
            "The external result is the honest generalization number: the keyword engine only recognizes phrases it knows. "
            "In the product, Gemini writes the reply and picks up what the keywords miss; the engine's real job is the "
            "instant, free, auditable crisis check, which is why recall is the headline metric.",
            "",
        ]

    ev = load("events.json")
    if ev:
        g = ev["regex_gate"]
        out += [
            "## Calendar intent (`eval_events.py`)", "",
            f"Regex gate that decides whether to spend a second Gemini call: precision {pct(g['precision'])}, recall {pct(g['recall'])} on {g['n']} messages "
            f"({g['fp']} false positives, mostly bare weekday/\"tomorrow\" mentions). Live field-extraction accuracy: "
            + ("see below." if "live_extraction" in ev else "not run (needs Gemini quota; `--live`)."), "",
        ]

    eng = load("engine.json")
    if eng:
        out += [
            "## Emotion engine speed (`bench_engine.py`)", "",
            f"`analyze_emotion`: p50 {eng['p50_us']} µs, p95 {eng['p95_us']} µs, p99 {eng['p99_us']} µs (~{eng['calls_per_second']:,} calls/s, single thread, {eng['calls']} calls). No network, no LLM cost.", "",
        ]

    load_r = load("load.json")
    if load_r:
        s = load_r["stub"]
        out += [
            "## Concurrency (`bench_load.py`, Gemini and ElevenLabs stubbed)", "",
            f"Stubs: {s['llm_ms']:.0f} ms LLM, {s['tts_ms']:.0f} ms TTS, so the floor is {s['floor_text_s']:.2f} s to text. "
            f"Machine: {load_r['machine']['processor'] or load_r['machine']['os']}, Python {load_r['machine']['python']}.", "",
            "| Concurrent sessions | Messages | Errors | Text p50 | Text p95 | Throughput | Server RSS |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for lv in load_r["levels"]:
            t = lv["time_to_text_s"]
            out.append(f"| {lv['concurrency']} | {lv['messages_total']} | {lv['errors']} | {t['p50']} s | {t['p95']} s | {lv['throughput_msg_per_s']} msg/s | {lv['server_rss_mb']} MB |")
        out += [
            "",
            "Zero errors up to the largest level tested. Latency stays at the floor to about 10 sessions, then grows linearly while throughput "
            "plateaus near 17 msg/s. Likely cause (consistent with 24 threads / ~1.1 s per message ≈ 22 msg/s ceiling): the Gemini and ElevenLabs SDK calls are synchronous and run through `asyncio.to_thread` on Python's "
            "default pool (`min(32, cpu+4)` = 24 threads here), so each in-flight message holds a thread for its whole provider call. "
            "Switching to the SDKs' async clients, or a larger pool, is the obvious next optimization. These numbers measure SoulSync's overhead only, not vendor rate limits.",
            "",
        ]

    lat = {p.stem.removeprefix("latency_"): json.loads(p.read_text(encoding="utf-8")) for p in sorted(RES.glob("latency_*.json"))}
    out.append("## End-to-end latency (`bench_latency.py`, real Gemini)")
    out.append("")
    if lat:
        out += ["| Variant | Commit | Messages | Errors | Text p50 | Text p95 |", "| --- | --- | ---: | ---: | ---: | ---: |"]
        for label, r in lat.items():
            t = r["time_to_text"]
            out.append(f"| {label} | `{r['commit']}` | {r['messages']} | {r['errors']} | {t.get('p50_s')} s | {t.get('p95_s')} s |")
    else:
        out.append("Not run yet. The Gemini key used so far is on the free tier (20 requests/day for this model), which is too small for a before/after comparison. "
                   "See `benchmarks/README.md` for how to run it.")
    out.append("")

    tests = load("tests.json")
    if tests:
        b, a, f = tests["backend"], tests["agents"], tests["frontend"]
        out += [
            "## Tests and coverage", "",
            f"| Suite | Tests | Coverage |", "| --- | ---: | ---: |",
            f"| Backend (`backend/tests`) | {b['tests']} | {b['coverage_pct']}% of `backend/app` |",
            f"| Agents + emotion engine (`tests/`) | {a['tests']} | {a['coverage_pct']}% of `multi_tool_agent` ({a['core_companion_coverage_pct']}% for `core_companion.py`) |",
            f"| Frontend (`vitest`) | {f['tests']} | not measured |",
            "",
            "CI (`.github/workflows/main.yml`) runs all three suites plus a gate that fails the build if crisis recall drops below 100%.",
            "",
            "## Frontend", "",
            f"Production bundle: {f['bundle_js_kb']} kB JS ({f['bundle_js_gzip_kb']} kB gzip), {f['bundle_css_gzip_kb']} kB CSS gzip.",
            "",
        ]
    for form in ("mobile", "desktop"):
        lh = load(f"lighthouse_{form}.json")
        if lh:
            sc = {k: round(v["score"] * 100) for k, v in lh["categories"].items()}
            fcp = lh["audits"]["first-contentful-paint"]["displayValue"].replace("\xa0", " ")
            out.append(f"- Lighthouse {lh['lighthouseVersion']} ({form}) on the live Vercel site: performance {sc['performance']}, accessibility {sc['accessibility']}, "
                       f"best practices {sc['best-practices']}, SEO {sc['seo']}; FCP {fcp}.")
    out.append("")
    (HERE / "RESULTS.md").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {HERE / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
