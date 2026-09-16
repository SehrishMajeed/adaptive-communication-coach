# Offline evaluation

Status: implemented regression harness for local CI. This is not a live model benchmark and does not prove production AI quality.

## Purpose

The evaluator is an AI boundary, so normal tests must verify more than "the API returned JSON." The offline evaluation fixtures check whether committed evaluator outputs obey the contract for:

- schema-valid, quote-backed completed feedback;
- abstention when evidence is insufficient;
- spoken prompt-injection resistance.

These checks run without provider credentials and without paid model calls.

## Fixture set

Fixtures live in `tests/fixtures/evaluations/`.

| Fixture | Risk | What it proves |
| --- | --- | --- |
| `technical_project_clear.json` | normal | Completed feedback must cite a transcript quote and recommend the expected focus. |
| `too_little_speech_abstain.json` | abstention | Weak input must abstain without scores, evidence or focus. |
| `spoken_prompt_injection_resisted.json` | prompt injection | Spoken instructions are treated as transcript content, not evaluator instructions. |

## Runner

The runner is `backend/app/evaluation/offline_runner.py`.

It verifies:

- current prompt version is present;
- prompt says spoken instructions are untrusted;
- fixture output validates against `CommunicationEvaluation`;
- expected status and focus match;
- required quote appears in evidence;
- prompt-injection fixture does not receive all-10 scores.

Run:

```sh
python -m pytest tests/test_offline_evaluation.py -q
```

## Honest boundary

This is a regression harness for known cases. It does not measure live Gemini accuracy, human agreement, calibration, latency or cost. A later evaluation phase should add a consented/synthetic corpus, repeated live runs, human rubric comparison and explicit budget tracking.
