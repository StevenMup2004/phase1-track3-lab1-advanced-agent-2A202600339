# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100_diverse.json
- Mode: live
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8 | 0.89 | 0.09 |
| Avg attempts | 1 | 1.3 | 0.3 |
| Avg token estimate | 1660.68 | 2322.74 | 662.06 |
| Avg latency (ms) | 3652.02 | 6796.94 | 3144.92 |

## Failure modes
```json
{
  "entity_drift": {
    "react": 19,
    "reflexion": 7
  },
  "wrong_final_answer": {
    "react": 18,
    "reflexion": 18
  },
  "incomplete_multi_hop": {
    "react": 12,
    "reflexion": 8
  },
  "looping": {
    "reflexion": 11
  },
  "none": {
    "react": 51,
    "reflexion": 56
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
This benchmark evaluated ReAct (single-attempt) and Reflexion (multi-attempt with reflection memory) agents on hotpot_100_diverse.json using real OpenAI API calls with gpt-4o-mini. ReAct achieved an exact-match (EM) accuracy of 80.00%, while Reflexion achieved 89.00%, yielding a delta of 0.0900. Reflexion's improvement comes from its ability to reflect on wrong answers, identify failure modes (such as entity_drift, incomplete_multi_hop, and wrong_final_answer), and feed concrete strategies back into the Actor via reflection memory. The structured evaluator provides detailed feedback including missing_evidence and spurious_claims, which gives the Reflector richer signal for diagnosis. The tradeoff is higher token consumption (662 tokens/question more on average) and increased latency (3145ms more). Key failure modes that persisted even after reflection include entity_drift (where the agent latches onto a plausible but incorrect entity from context) and looping (where reflection does not surface a novel strategy). Future improvements could include adaptive_max_attempts (stop early if reflection quality declines) and memory_compression (summarize long reflection histories to stay within context limits).
