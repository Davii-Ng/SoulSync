"""Unit tests for the real emotion engine (no stubs, no network)."""

import json
from pathlib import Path

import pytest

from multi_tool_agent import core_companion

# Resolve the functions at call time: test_backend_connection.py patches these names at
# import time and only restores them in its teardown, so `from ... import analyze_emotion`
# at collection time would bind a mock.


def analyze_emotion(text: str) -> dict:
    return core_companion.analyze_emotion(text)


def suggest_resource(emotion: str, severity: str = "medium") -> dict:
    return core_companion.suggest_resource(emotion, severity)


DATASETS = Path(__file__).resolve().parent.parent / "benchmarks" / "datasets"


def _load(name: str) -> list[dict]:
    with open(DATASETS / name, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@pytest.mark.parametrize("row", _load("crisis.jsonl"), ids=lambda r: r["text"][:40])
def test_every_labeled_crisis_phrase_is_flagged(row):
    """Safety gate: a missed crisis message is the worst failure this engine can have."""
    result = analyze_emotion(row["text"])
    assert result["crisis"] is True
    assert result["emotion"] == "crisis"
    assert result["severity"] == "critical"


@pytest.mark.parametrize("text", [
    "I'm not angry at all.",
    "I don't feel nervous anymore.",
    "I'm not worried about it, honestly.",
])
def test_negated_emotion_is_not_reported(text):
    result = analyze_emotion(text)
    assert result["emotion"] not in ("angry", "anxious")


def test_mixed_emotions_return_secondary():
    result = analyze_emotion("I'm furious and honestly heartbroken about what happened.")
    assert result["emotion"] == "angry"
    assert result["secondary_emotion"] == "sad"


def test_no_signal_is_neutral_with_low_confidence():
    result = analyze_emotion("I bought groceries.")
    assert result["emotion"] == "neutral"
    assert result["confidence"] <= 0.5
    assert result["crisis"] is False


@pytest.mark.parametrize("text, expected", [
    ("a bit tired but fine", "low"),
    ("I'm overwhelmed and exhausted", "medium"),
    ("burned out, completely exhausted, falling apart", "high"),
])
def test_severity_scales_with_keyword_weight(text, expected):
    assert analyze_emotion(text)["severity"] == expected


@pytest.mark.parametrize("text", [
    "I'm cutting myself some slack today.",
    "That video had me killing myself laughing.",
    "I'm ending my lifelong habit of procrastinating.",
])
def test_benign_idioms_are_not_crisis(text):
    assert analyze_emotion(text)["crisis"] is False


@pytest.mark.parametrize("text", [
    "I overdosed last year and I'm scared I'll do it again.",
    "I keep self-harming.",
    "I cut myself some slack but then I cut myself again.",
])
def test_inflections_and_mixed_idioms_still_flag_crisis(text):
    assert analyze_emotion(text)["crisis"] is True


def test_single_passive_phrase_alone_is_not_crisis():
    assert analyze_emotion("what's the point of arguing with a thermostat")["crisis"] is False


def test_two_passive_phrases_escalate_to_crisis():
    result = analyze_emotion("what's the point, no one would miss me")
    assert result["crisis"] is True


@pytest.mark.parametrize("emotion", ["stressed", "anxious", "sad", "angry", "happy", "calm", "neutral", "crisis"])
@pytest.mark.parametrize("severity", ["low", "medium", "high"])
def test_suggest_resource_covers_every_label_and_severity(emotion, severity):
    result = suggest_resource(emotion, severity)
    assert result["suggestion"] and result["follow_up"]


def test_crisis_suggestion_mentions_988():
    assert "988" in suggest_resource("crisis", "high")["suggestion"]


def test_unknown_emotion_falls_back_to_neutral_copy():
    assert suggest_resource("bewildered")["suggestion"] == suggest_resource("neutral")["suggestion"]
