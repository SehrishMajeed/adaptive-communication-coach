# 8. Agentic Evaluation Pipeline in CI

Date: 2026-09-16

## Status

Accepted

## Context

As the backend evaluation engine grew to use Gemini structured outputs, we needed a way to prove that the AI evaluator consistently applies the grading rubric, resists prompt injections, and abstains when audio quality is too low. Initially, we relied on an offline validation harness (`offline_runner.py`) that mocked the LLM response with JSON fixtures. While this proved that our *Python code* handles valid/invalid LLM outputs correctly, it did not prove that the *LLM itself* behaves as expected when given raw audio transcripts. 

We needed a repeatable, automated way to benchmark the actual live behavior of the LLM against a known golden dataset of audio inputs without incurring continuous high API costs or breaking traditional, deterministic unit tests.

## Decision

We will implement a dedicated Agentic Evaluation Pipeline (`evaluate_agent.py`) that runs against a synthesized audio corpus. 

1. **Isolation from traditional CI**: The agentic evaluation runs as a manually triggered GitHub Action (`Agentic AI Evaluation`), isolated from the main unit test suite. This ensures that network timeouts, API quota limits, missing secrets or LLM non-determinism do not falsely fail standard CI/CD checks for business logic.
2. **Synthetic Corpus**: The pipeline evaluates the live model against `.wav` files mapped to expected scenario baselines in `tests/corpus/` (e.g., `bad_audio_abstain.json`). 
3. **Graceful Degradation**: If `GEMINI_API_KEY` is not present, the script writes an explicit skipped report and exits cleanly without attempting a provider call.
4. **Metrics Generation**: The script produces a final `evaluation_report.md` artifact detailing accuracy, abstention rates, and latency per request.

## Consequences

- **Positive**: We now have a documented, repeatable benchmark entry point for live LLM performance. Prompt engineering changes or model version bumps can be evaluated intentionally against the corpus before release decisions.
- **Positive**: Standard unit tests remain fast, deterministic, and free to run offline.
- **Negative**: Creating and maintaining a high-quality synthetic audio corpus takes time. Changes to the rubric require updating both the application and the expected outcomes in the evaluation corpus.
