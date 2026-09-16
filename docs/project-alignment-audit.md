# Project alignment audit

Status: implementation and product judgment snapshot for the current repository. This is an evidence-based planning document, not proof of live Gemini behavior or user demand.

Generated: 2026-09-16

## Executive judgment

The project is now pointed at a real pain:

> Technical people often know their work but cannot make the explanation land for a listener who lacks their context.

The strongest product shape is not a generic public-speaking app. It is a private, fast, high-stakes explanation rehearsal loop:

> record one technical explanation, get one evidence-backed improvement target, retry the same task, and compare honestly.

The codebase is correctly moving toward that direction, especially around audio-only upload, bounded Gemini output, transcript-based deterministic metrics, local video review, in-memory retry comparison, and honest non-production documentation. It still does not deliver the full painkiller loop: explicit audience/task setup, one drill as a durable intervention, ownership, or evidence-backed progress.

As a portfolio artifact, the project should communicate:

> CS student focused on AI engineering, agentic systems, and building practical AI products with Python, React, and modern AI tools.

The repo mostly supports that positioning already. It has a real AI product wedge, Python/FastAPI backend, React frontend, Gemini integration, LangGraph workflow seam, validation tests, architecture docs, and a prototype retry comparison loop. The honest current claim is: practical AI product with a credible path toward agentic coaching. The main danger is overclaiming agentic or production capability before durable interventions, ownership, migrations, and evidence validation exist.

## Alignment scorecard

| Area | Current alignment | Judgment |
| --- | --- | --- |
| User pain | Strong in docs; partially visible in UI | The thesis is sharp, but the app still feels like a prototype feedback form. |
| Product loop | Baseline recording, feedback, and in-memory retry comparison exist | Durable intervention persistence is not implemented. |
| Privacy promise | Good technical direction | Video stays local by design, but manual browser verification remains incomplete. |
| AI boundary | Good for Phase 1 | Gemini is schema-bounded and forbidden from metrics/visual claims, but evidence spans and prompt versioning are still missing. |
| Architecture | Appropriate modular monolith | Phase 2 needs Alembic, ownership, session context, measurement/evaluation split. |
| Setup | Good local/CI baseline | Runtime dependencies are unpinned and live Gemini/device path is not verified. |
| Android ambition | Directionally valid later | Do not start Android until the backend loop is truthful and manually verified. |

## What is already aligned

- `docs/product-thesis.md` defines a narrow painkiller wedge instead of a broad coaching fantasy.
- `README.md` accurately says the prototype is not production-ready and avoids claiming personalized progress.
- `frontend/services/recording.ts` records local video and a separate audio track, supporting the privacy boundary.
- `frontend/services/audio.ts` decodes and re-encodes mono PCM16 WAV before upload.
- `backend/app/services/media.py` rejects unsupported media before Gemini.
- `backend/app/services/llm_provider.py` tells Gemini not to evaluate body language, confidence, pace, filler counts, or word counts.
- `backend/app/domain/evaluation.py` bounds rubric scores and forbids unexpected provider fields.
- `frontend/types.ts` validates the backend response before rendering.
- Tests cover mocked provider behavior, invalid media, schema boundaries, frontend parsing, and build/typecheck.

## Misalignment and risk list

### P0 gate: manual acceptance is still incomplete

Phase 2 architecture should not begin until `docs/pr1-manual-verification.md` is completed with a valid backend Gemini key and real Chrome DevTools evidence.

Why it matters:

- The product is built around trust.
- If audio-only upload or live Gemini rendering fails in a real browser, schema work would be premature.

### P1: the app does not yet complete the core painkiller loop

Current implementation:

- record;
- review;
- get scores/suggestions;
- restart.

Painkiller loop needed:

- record;
- identify one priority;
- give one drill;
- retry same explanation;
- compare the same target.

The latest UI copy, deterministic drill mapping, and in-memory retry comparison improve the feel, but durable comparison remains Phase 4 work after ownership/domain architecture.

### P1: task context is hardcoded

Backend uses one fixed scenario:

```text
Explain a technical project to a non-technical person in 60 seconds.
```

This is acceptable for PR 1. It becomes a blocker before personalization because the product thesis requires audience and goal to be part of the task context.

### P1: persistence does not match target domain

`CoachingAttempt` still contains transcript, measurements, and evaluations in one flattened table. This is intentionally pre-Phase-2, but it should not be extended further.

Next schema must split:

- user ownership;
- practice session/task context;
- attempt lifecycle;
- measurement sets;
- evaluations.

### P1: prompt is safe but not yet evidence-grounded

Current prompt is good for safety:

- treats spoken instructions as untrusted;
- asks for verbatim transcript;
- forbids visual/confidence/pacing/filler claims;
- uses structured response schema.

Missing for the future:

- prompt version constant;
- rubric version constant;
- evidence references or quoted transcript spans;
- abstention/status field;
- model/provider metadata in persisted records.

Do not add evidence claims to the UI before schema supports them.

### P2: setup is functional but not release-grade

- Python requirements are unpinned.
- Runtime and dev requirements are minimal but not locked.
- SQLite import-time schema creation remains.
- There is no Alembic.
- No rate limiting or cost tracking exists.
- No auth/ownership exists.

These are not blockers for the local prototype, but they are blockers for public/shared deployment.

## Prompt and AI assessment

### Current prompt grade: B for Phase 1, C for product vision

Strengths:

- clear task;
- schema-enforced output;
- explicit untrusted user content boundary;
- explicit forbidden claim list;
- graceful provider failure boundary.

Weaknesses:

- inline prompt has no named version;
- scenario is hardcoded;
- no rubric anchors for what 0, 5, or 10 mean;
- no evidence spans;
- no abstention field;
- no usage/cost metadata capture;
- temperature is `0.2`, so do not claim deterministic behavior.

Minimum next prompt improvement, when Phase 3 begins:

1. Move prompt text/version into a named constant or prompt module.
2. Add rubric anchors for clarity, structure, conciseness, and audience awareness.
3. Add evaluation status such as `valid`, `low_audio_quality`, `insufficient_speech`, or `abstained`.
4. Add evidence references after the domain schema can store them.
5. Store provider/model/prompt/schema versions with each evaluation.

## Tech stack judgment

The current stack is appropriate:

- React + Vite is enough for the web proof of capture/evaluation.
- FastAPI + SQLAlchemy is enough for the API and domain model.
- LangGraph is acceptable only if it continues to model real branching: invalid input, baseline, retry, abstention, comparison.
- Gemini behind a provider adapter is the right boundary.
- SQLite is fine for local development, but PostgreSQL plus Alembic must own production schema evolution.

Do not add:

- microservices;
- vector database;
- RAG;
- PyTorch/fine-tuning;
- social/community features;
- body-language inference;
- Android app before the backend loop is verified.

## Step-by-step execution order

1. Complete PR 1 manual verification in Chrome with DevTools and valid Gemini key.
2. Fix any manual verification failures before architecture work.
3. Implement PR 2A: Alembic and domain schema only.
4. Implement anonymous ownership and session context.
5. Implement same-session retry comparison for the fixed 60-second explanation.
6. Add evidence-grounded evaluator status and prompt/rubric versioning.
7. Add Android-first UX only after the backend loop is real.

## Acceptance criteria for “aligned enough to proceed”

The project is aligned enough for Phase 2 only when:

- real browser upload is proven audio-only;
- valid Gemini key produces a renderable response;
- recording permissions and auto-stop work manually;
- failed provider/backend paths preserve local review;
- database remains free of profile mutations in PR 1;
- all automated tests pass.

Until then, the correct answer to “is it ready for Phase 2?” is:

> Not yet. The product direction is right, but the live browser/provider path is still unverified.

## Highest-leverage simplification

Keep one scenario, one audience, four rubric dimensions, and one retry loop until users prove the pain is real.

Any broader product expansion before that is likely overbuilding.
