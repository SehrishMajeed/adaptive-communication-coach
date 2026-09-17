# Project alignment audit

Status: historical implementation and product judgment snapshot generated before the later durable-session, evidence-grounded, workflow-routing and Android-shell milestones. Keep it as an audit artifact, not as the current source of truth. Current status is summarized in the root README, target architecture and implementation plan.

Generated: 2026-09-16

## Executive judgment

The project is now pointed at a real pain:

> Technical people often know their work but cannot make the explanation land for a listener who lacks their context.

The strongest product shape is not a generic public-speaking app. It is a private, fast, high-stakes explanation rehearsal loop:

> record one technical explanation, get one evidence-backed improvement target, retry the same task, and compare honestly.

The codebase is correctly moving toward that direction, especially around audio-only upload, bounded Gemini output, transcript-based deterministic metrics, local video review, durable session-scoped retry comparison, explicit practice setup and honest non-production documentation. It still does not prove live Gemini quality, real-device Android media reliability, production release readiness or user demand.

As a portfolio artifact, the project should communicate:

> CS student focused on AI engineering, agentic systems, and building practical AI products with Python, React, and modern AI tools.

The repo supports that positioning with a real AI product wedge, Python/FastAPI backend, React frontend, React Native Android shell, Gemini integration boundary, workflow seam, validation tests, architecture docs, durable interventions, evidence validation and backend-owned retry comparison. The honest current claim is: practical AI product with a credible path toward agentic coaching. The main danger is now overclaiming production deployment, live model reliability, real-device compatibility or long-term adaptive learning before those gates are verified.

## Alignment scorecard

| Area | Current alignment | Judgment |
| --- | --- | --- |
| User pain | Strong in docs; partially visible in UI | The thesis is sharp, but the app still feels like a prototype feedback form. |
| Product loop | Baseline recording, feedback, durable intervention and backend-owned retry comparison exist | Long-term adaptive profile updates are not implemented. |
| Privacy promise | Good technical direction | Video stays local by design, but manual browser verification remains incomplete. |
| AI boundary | Stronger than Phase 1 | Gemini is schema-bounded, evidence-grounded and versioned, but live reliability benchmarks remain unverified. |
| Architecture | Appropriate modular monolith | Durable sessions, Alembic, ownership and workflow routes exist; production deployment/retention work remains. |
| Setup | Good local/CI baseline | CI is green; live Gemini/device path is not verified. |
| Android ambition | Implemented shell, not release-ready | Continue Android hardening before any Play Store claim. |

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

### P0 gate: live manual acceptance is still incomplete

Durable architecture has proceeded through deterministic tests, but live manual acceptance still requires `docs/pr1-manual-verification.md` to be completed with a valid backend Gemini key and real Chrome DevTools/device evidence.

Why it matters:

- The product is built around trust.
- If audio-only upload or live Gemini rendering fails in a real browser, schema work would be premature.

### P1: the app still needs real-device proof of the core painkiller loop

Current implementation includes record, review, one target, drill, retry and backend-owned comparison. The remaining risk is not the code shape; it is proving that the loop works on real devices with real backend credentials and acceptable latency/failure behavior.

### P1: task context is explicit but not yet user-validated

The web and backend now support scenario, audience and goal setup. The next product risk is whether users understand and value that setup quickly enough in a mobile flow.

### P1: persistence supports the target domain but release policy remains incomplete

The durable schema now separates owned practice sessions, attempts, evaluations, measurements, interventions, comparisons and workflow audit fields. The remaining production work is retention/deletion policy, managed database deployment and privacy-reviewable operational behavior.

### P1: prompt is evidence-grounded but not live-benchmarked

Current prompt is good for safety:

- treats spoken instructions as untrusted;
- asks for verbatim transcript;
- forbids visual/confidence/pacing/filler claims;
- uses structured response schema.

Remaining future work:

- budgeted live reliability runs;
- human rubric comparison;
- latency/cost reporting;
- held-out corpus versioning.

### P2: setup is improved but not release-grade

- No production deployment path is selected.
- No managed database, backup/restore or migration rollout is rehearsed.
- No rate limiting or cost tracking exists.
- Anonymous owner tokens are not a full authentication system.
- Real-device recording, signed release and Play Console rollout remain unverified.

These are not blockers for the local prototype, but they are blockers for public/shared deployment.

## Prompt and AI assessment

### Current prompt grade: B+ for the prototype, incomplete for production evidence

Strengths:

- clear task;
- schema-enforced output;
- explicit untrusted user content boundary;
- explicit forbidden claim list;
- graceful provider failure boundary.

Weaknesses:

- no live repeated-run stability benchmark;
- no human-agreement report;
- no usage/cost metadata report from live provider calls;
- no calibrated confidence claim.

Minimum next AI-quality improvement:

1. Run the manual live Gemini checklist with approved credentials.
2. Add a small synthetic/consented live evaluation report with denominators and failures.
3. Compare repeated runs for stability before changing prompts.
4. Add cost/latency logging before any shared beta.

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
- long-term adaptive profile claims before evidence-gated profile logic is implemented.

## Step-by-step execution order

1. Complete live browser and Android device verification with valid backend Gemini credentials.
2. Fix any media, latency, provider or API failures before expanding features.
3. Add production guardrails: rate limits, cost limits, retention/deletion and deployment smoke.
4. Run a small user/pilot validation before claiming learning outcomes.
5. Add adaptive profile updates only after evidence and user behavior justify them.

## Acceptance criteria for “aligned enough to proceed”

The project is aligned enough for release hardening only when:

- real browser and Android upload are proven audio-only;
- valid Gemini key produces renderable responses with acceptable latency;
- recording permissions and cleanup work manually on real devices;
- failed provider/backend paths preserve local review;
- adaptive profile mutations remain blocked until evidence-gated policy exists;
- all automated tests and selected release checks pass.

Until then, the correct answer to "is it ready for public beta?" is:

> Not yet. The product direction and deterministic engineering are strong, but live provider, real-device and release-path evidence are still unverified.

## Highest-leverage simplification

Keep one scenario, one audience, four rubric dimensions, and one retry loop until users prove the pain is real.

Any broader product expansion before that is likely overbuilding.
