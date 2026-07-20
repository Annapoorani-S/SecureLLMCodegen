"""
Unit tests for the Groq LLM client retry and fallback behavior.
"""

from types import SimpleNamespace

import pytest

from src import llm_client


def _groq_response(text: str):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=text)
            )
        ]
    )


class _FakeCompletions:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return _groq_response(outcome)


def _fake_client(outcomes):
    completions = _FakeCompletions(outcomes)
    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=completions
        ),
        completions=completions,
    )


def test_call_groq_retries_rate_limits_then_falls_back(monkeypatch):
    fake_client = _fake_client(
        [
            Exception("429 rate limit exceeded"),
            Exception("429 rate limit exceeded"),
            "generated code",
        ]
    )

    monkeypatch.setattr(llm_client, "client", fake_client)
    monkeypatch.setattr(llm_client, "_MODEL_CHAIN", ["primary-model", "fallback-model"])
    monkeypatch.setattr(llm_client.time, "sleep", lambda _: None)

    result = llm_client._call_groq(
        "system prompt",
        "user requirement",
        max_retries=2,
    )

    assert result == "generated code"
    assert [call["model"] for call in fake_client.completions.calls] == [
        "primary-model",
        "primary-model",
        "fallback-model",
    ]


def test_call_groq_raises_non_rate_limit_errors_without_retry(monkeypatch):
    fake_client = _fake_client([ValueError("bad request")])

    monkeypatch.setattr(llm_client, "client", fake_client)
    monkeypatch.setattr(llm_client, "_MODEL_CHAIN", ["primary-model", "fallback-model"])

    with pytest.raises(ValueError, match="bad request"):
        llm_client._call_groq(
            "system prompt",
            "user requirement",
            max_retries=2,
        )

    assert len(fake_client.completions.calls) == 1
