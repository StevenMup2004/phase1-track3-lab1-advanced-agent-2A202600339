from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

from rich import print as rprint

from .llm_runtime import actor_answer, evaluator, reflector
from .schemas import AttemptTrace, QAExample, ReflectionEntry, RunRecord
from .utils import normalize_answer


def _detect_failure_mode(
    example: QAExample,
    predicted: str,
    gold: str,
    attempts: int,
    max_attempts: int,
) -> str:
    """Heuristic failure-mode classification based on answer analysis."""
    pred_norm = normalize_answer(predicted)
    gold_norm = normalize_answer(gold)

    if pred_norm == gold_norm:
        return "none"

    # Check for looping: if agent used all attempts and still wrong
    if attempts >= max_attempts and max_attempts > 1:
        # Could be looping or reflection_overfit
        return "looping"

    # Check for entity drift: answer contains a real entity but wrong one
    gold_tokens = set(gold_norm.split())
    pred_tokens = set(pred_norm.split())
    overlap = gold_tokens & pred_tokens

    if len(overlap) > 0 and len(overlap) < len(gold_tokens):
        return "incomplete_multi_hop"

    if len(pred_norm) > 0 and len(overlap) == 0:
        return "entity_drift"

    return "wrong_final_answer"


@dataclass
class BaseAgent:
    agent_type: Literal["react", "reflexion"]
    max_attempts: int = 1

    def run(self, example: QAExample) -> RunRecord:
        reflection_memory: list[str] = []
        reflections: list[ReflectionEntry] = []
        traces: list[AttemptTrace] = []
        final_answer = ""
        final_score = 0

        for attempt_id in range(1, self.max_attempts + 1):
            # ── Actor: generate answer ──
            answer, actor_tokens, actor_latency = actor_answer(
                example, attempt_id, self.agent_type, reflection_memory
            )

            # ── Evaluator: judge answer (structured) ──
            judge, eval_tokens, eval_latency = evaluator(example, answer)

            # Real token count and latency from API
            token_estimate = actor_tokens + eval_tokens
            latency_ms = actor_latency + eval_latency

            trace = AttemptTrace(
                attempt_id=attempt_id,
                answer=answer,
                score=judge.score,
                reason=judge.reason,
                token_estimate=token_estimate,
                latency_ms=latency_ms,
            )

            final_answer = answer
            final_score = judge.score

            if judge.score == 1:
                traces.append(trace)
                break

            # ── Reflexion loop: reflect on failure and update memory ──
            if self.agent_type == "reflexion" and attempt_id < self.max_attempts:
                ref_entry, ref_tokens, ref_latency = reflector(
                    example, attempt_id, judge, answer
                )
                # Update token/latency to include reflector cost
                trace.token_estimate += ref_tokens
                trace.latency_ms += ref_latency
                trace.reflection = ref_entry

                # Build memory string for actor to use next time
                memory_line = (
                    f"[Failure] {ref_entry.failure_reason} "
                    f"[Lesson] {ref_entry.lesson} "
                    f"[Strategy] {ref_entry.next_strategy}"
                )
                reflection_memory.append(memory_line)
                reflections.append(ref_entry)

            traces.append(trace)

        total_tokens = sum(t.token_estimate for t in traces)
        total_latency = sum(t.latency_ms for t in traces)

        failure_mode = _detect_failure_mode(
            example, final_answer, example.gold_answer,
            len(traces), self.max_attempts,
        )

        return RunRecord(
            qid=example.qid,
            question=example.question,
            gold_answer=example.gold_answer,
            agent_type=self.agent_type,
            predicted_answer=final_answer,
            is_correct=bool(final_score),
            attempts=len(traces),
            token_estimate=total_tokens,
            latency_ms=total_latency,
            failure_mode=failure_mode,
            reflections=reflections,
            traces=traces,
        )


class ReActAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(agent_type="react", max_attempts=1)


class ReflexionAgent(BaseAgent):
    def __init__(self, max_attempts: int = 3) -> None:
        super().__init__(agent_type="reflexion", max_attempts=max_attempts)
