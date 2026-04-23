# Lab 16 — Reflexion Agent
**Name**: Vu Hai Dang - 2A202600339
Repo này xây dựng và đánh giá **Reflexion Agent** trên bộ dữ liệu HotpotQA, sử dụng OpenAI API thật (`gpt-4o-mini`).

## 1. Tổng quan

Hệ thống gồm 2 agent:
- **ReAct Agent**: Trả lời câu hỏi multi-hop trong 1 lần thử duy nhất.
- **Reflexion Agent**: Nếu trả lời sai, tự phân tích lỗi (reflect), rút ra bài học, và thử lại (tối đa 3 lần).

Pipeline gồm 3 thành phần LLM:
1. **Actor** — Đọc context và trả lời câu hỏi.
2. **Evaluator** — So sánh câu trả lời với đáp án, trả JSON có cấu trúc (structured evaluator).
3. **Reflector** — Phân tích lỗi và đề xuất chiến lược cho lần thử tiếp theo.

## 2. Những việc đã thực hiện

### Core Flow (80 điểm)

| Công việc | File | Mô tả |
|---|---|---|
| Hoàn thiện Schemas | `src/reflexion_lab/schemas.py` | Định nghĩa `JudgeResult` (score, reason, missing_evidence, spurious_claims) và `ReflectionEntry` (attempt_id, failure_reason, lesson, next_strategy). Thêm field `type` vào `QAExample` cho dataset đa dạng. |
| Viết System Prompts | `src/reflexion_lab/prompts.py` | 3 prompt cho Actor (multi-hop reasoning, 1-5 từ), Evaluator (JSON output), Reflector (failure analysis JSON). |
| Tạo LLM Runtime | `src/reflexion_lab/llm_runtime.py` | **File mới** — Thay thế `mock_runtime.py`. Gọi OpenAI API (`gpt-4o-mini`), đo token thực tế từ `response.usage`, đo latency bằng `time.perf_counter()`. |
| Triển khai Reflexion Loop | `src/reflexion_lab/agents.py` | Implement vòng lặp: Actor → Evaluator → (nếu sai) Reflector → cập nhật memory → Actor thử lại. Tự phân loại failure mode (entity_drift, incomplete_multi_hop, wrong_final_answer, looping). |
| Cập nhật Reporting | `src/reflexion_lab/reporting.py` | Failure modes theo loại (≥3 keys), discussion tự sinh (≥250 ký tự), mode `"live"`. |
| Cập nhật Benchmark | `run_benchmark.py` | Default dataset: `data/hotpot_100_diverse.json`, thêm progress logging. |

### Bonus Features (20 điểm)

| Feature | Mô tả |
|---|---|
| `structured_evaluator` (10đ) | Evaluator trả về JSON có cấu trúc gồm `score`, `reason`, `missing_evidence`, `spurious_claims` thay vì chỉ 0/1. |
| `reflection_memory` (10đ) | Reflexion Agent lưu lại bài học từ mỗi lần thử sai và feed vào Actor prompt cho lần thử tiếp theo. |

### Dataset

- Sử dụng **100 mẫu thật** từ bộ HotpotQA (Hugging Face Datasets).
- Đa dạng độ khó: Easy (33), Medium (33), Hard (34).
- Đa dạng loại câu hỏi: Bridge (51) và Comparison (49).
- File: `data/hotpot_100_diverse.json`

### Báo cáo phân tích

- `outputs/sample_run/report.json` — Báo cáo benchmark đầy đủ.
- `outputs/sample_run/report.md` — Báo cáo markdown tổng hợp.
- `outputs/sample_run/analysis_by_difficulty.md` — Phân tích chi tiết theo độ khó, loại câu hỏi, failure modes, và ví dụ cụ thể.

## 3. Kết quả Benchmark

| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM Accuracy | 80.0% | 89.0% | +9.0% |
| Avg Attempts | 1.0 | 1.3 | +0.3 |
| Avg Tokens | 1,661 | 2,323 | +662 |
| Avg Latency | 3,652ms | 6,797ms | +3,145ms |

### Theo độ khó

| Difficulty | ReAct EM | Reflexion EM | Delta |
|---|---:|---:|---:|
| Easy | 81.8% | 93.9% | +12.1% |
| Medium | 82.3% | 88.2% | +5.9% |
| Hard | 75.8% | 84.9% | +9.1% |

## 4. Điểm Autograder

```
Auto-grade total: 100/100
- Flow Score (Core): 80/80
  * Schema: 30/30
  * Experiment: 30/30
  * Analysis: 20/20
- Bonus Score: 20/20
```

## 5. Cách chạy

```bash
# Cài đặt môi trường
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Cấu hình API key (tạo file .env)
echo OPENAI_API_KEY=sk-your-key-here > .env

# Chạy benchmark (100 mẫu, ~20 phút)
python run_benchmark.py --dataset data/hotpot_100_diverse.json --out-dir outputs/sample_run

# Chạy chấm điểm tự động
python autograde.py --report-path outputs/sample_run/report.json

# Tạo báo cáo phân tích theo độ khó
python generate_analysis.py
```

## 6. Cấu trúc mã nguồn

```
├── src/reflexion_lab/
│   ├── schemas.py          # Định nghĩa kiểu dữ liệu (QAExample, JudgeResult, ReflectionEntry, ...)
│   ├── prompts.py          # System prompts cho Actor, Evaluator, Reflector
│   ├── llm_runtime.py      # [MỚI] OpenAI API runtime (thay thế mock_runtime.py)
│   ├── mock_runtime.py     # [CŨ] Logic mock giả lập (không còn sử dụng)
│   ├── agents.py           # ReAct Agent + Reflexion Agent với Reflexion loop
│   ├── reporting.py        # Logic xuất báo cáo benchmark
│   └── utils.py            # Tiện ích (normalize_answer, load_dataset, save_jsonl)
├── data/
│   ├── hotpot_100_diverse.json  # 100 mẫu HotpotQA thật (đa dạng độ khó + loại)
│   └── hotpot_mini.json         # 8 mẫu gốc (scaffold)
├── outputs/sample_run/
│   ├── report.json              # Báo cáo benchmark JSON
│   ├── report.md                # Báo cáo benchmark Markdown
│   ├── analysis_by_difficulty.md # Phân tích chi tiết theo độ khó
│   ├── react_runs.jsonl         # Kết quả chạy ReAct
│   └── reflexion_runs.jsonl     # Kết quả chạy Reflexion
├── run_benchmark.py        # Script chính chạy benchmark
├── autograde.py            # Công cụ chấm điểm tự động
├── generate_analysis.py    # Script tạo báo cáo phân tích
└── requirements.txt        # Dependencies (pydantic, rich, typer, openai, ...)
```
