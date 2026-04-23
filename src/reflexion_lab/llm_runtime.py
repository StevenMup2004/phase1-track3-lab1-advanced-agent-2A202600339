"""OpenAI LLM Runtime — replaces mock_runtime.py with real API calls.

Uses gpt-4o-mini for cost efficiency. Tracks actual token usage and latency.
"""
from __future__ import annotations

import json
import os
import time
from typing import Tuple

from dotenv import load_dotenv
from openai import OpenAI

from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import JudgeResult, QAExample, ReflectionEntry

# ── bootstrap ──────────────────────────────────────────────────────────
load_dotenv()

_client: OpenAI | None = None

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _get_client() -> OpenAI:
    """Lazy-init singleton so import alone never raises."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


# ── helpers ────────────────────────────────────────────────────────────

def _build_context_text(example: QAExample) -> str:
    """Flatten context chunks into a numbered text block."""
    parts: list[str] = []
    for i, chunk in enumerate(example.context, 1):
        parts.append(f"[{i}] {chunk.title}: {chunk.text}")
    return "\n".join(parts)


def _chat(system: str, user: str, temperature: float = 0.0) -> Tuple[str, int, int]:
    """Call OpenAI chat and return (content, total_tokens, latency_ms)."""
    client = _get_client()
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=512,
    )
    latency_ms = int((time.perf_counter() - t0) * 1000)
    content = resp.choices[0].message.content or ""
    total_tokens = resp.usage.total_tokens if resp.usage else 0
    return content, total_tokens, latency_ms


def _parse_json(text: str) -> dict:
    """Best-effort JSON extraction from LLM output."""
    text = text.strip()
    # Try to find JSON object in text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return {}


# ── public API (same signatures as mock_runtime) ──────────────────────

def actor_answer(
    example: QAExample,
    attempt_id: int,
    agent_type: str,
    reflection_memory: list[str],
) -> Tuple[str, int, int]:
    """Ask the Actor to answer a multi-hop question.

    Returns (answer_text, tokens_used, latency_ms).
    """
    context_text = _build_context_text(example)

    user_msg = f"Question: {example.question}\n\nContext:\n{context_text}"

    if reflection_memory:
        memory_text = "\n".join(
            f"- Attempt {i+1}: {m}" for i, m in enumerate(reflection_memory)
        )
        user_msg += f"\n\nReflection notes from previous attempts:\n{memory_text}"
        user_msg += "\n\nApply the strategies above to avoid repeating mistakes."

    content, tokens, latency = _chat(ACTOR_SYSTEM, user_msg)
    # Clean up answer — strip quotes, whitespace, periods
    answer = content.strip().strip('"').strip("'").rstrip(".")
    return answer, tokens, latency


def evaluator(
    example: QAExample,
    answer: str,
) -> Tuple[JudgeResult, int, int]:
    """Use the structured Evaluator to judge an answer.

    Returns (JudgeResult, tokens_used, latency_ms).
    """
    user_msg = (
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Predicted answer: {answer}"
    )
    content, tokens, latency = _chat(EVALUATOR_SYSTEM, user_msg)
    data = _parse_json(content)

    return JudgeResult(
        score=int(data.get("score", 0)),
        reason=data.get("reason", content[:200]),
        missing_evidence=data.get("missing_evidence", []),
        spurious_claims=data.get("spurious_claims", []),
    ), tokens, latency


def reflector(
    example: QAExample,
    attempt_id: int,
    judge: JudgeResult,
    wrong_answer: str,
) -> Tuple[ReflectionEntry, int, int]:
    """Analyze a failed attempt and produce reflection.

    Returns (ReflectionEntry, tokens_used, latency_ms).
    """
    user_msg = (
        f"Question: {example.question}\n"
        f"Agent's answer: {wrong_answer}\n"
        f"Correct answer: {example.gold_answer}\n"
        f"Evaluator feedback: {judge.reason}\n"
        f"Missing evidence: {judge.missing_evidence}"
    )
    content, tokens, latency = _chat(REFLECTOR_SYSTEM, user_msg)
    data = _parse_json(content)

    return ReflectionEntry(
        attempt_id=attempt_id,
        failure_reason=data.get("failure_reason", judge.reason),
        lesson=data.get("lesson", "Need to re-examine context more carefully."),
        next_strategy=data.get("next_strategy", "Re-read all context paragraphs and trace the reasoning chain step by step."),
    ), tokens, latency
