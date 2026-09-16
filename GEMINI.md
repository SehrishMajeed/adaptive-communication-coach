# GEMINI.md — Adaptive Communication Coach Integration Rules

Status: project-specific operating guide. This file adapts the hardening spirit of the supplied template to this repository only. It must not be treated as evidence that live Gemini behavior, production deployment, retention settings, or Play Store readiness have been verified.

## Project Goal

Aura Coach is a privacy-conscious communication practice prototype for technical people who need to explain complex work clearly in high-stakes moments.

Current wedge:

> Explain a technical project to a recruiter or nontechnical listener in 60 seconds, receive one evidence-backed improvement target, retry, and compare honestly.

## Current Gemini Boundary

- Provider code lives in `backend/app/services/llm_provider.py`.
- The backend calls Gemini through the server only; frontend code must never contain provider keys.
- Current model in code: `gemini-2.5-flash`.
- Current generation temperature in code: `0.2`.
- Current provider timeout: 45 seconds, one SDK attempt.
- Raw audio is sent to the provider only after server-side WAV validation.
- The LLM must not be asked to calculate deterministic metrics such as duration, word count, WPM, or filler counts.
- The LLM must not assess body language, appearance, eye contact, posture, confidence, or visual engagement in the initial product.

If the model name, temperature, prompt, schema, timeout, retry policy, or provider SDK changes, update this file, the relevant tests, and the README limitations in the same change.

## Hardening Directives and Operating Invariants

### 1. Managed-Memory and Resource Safety

- This is a Python/TypeScript project, not a Rust engine. Do not copy Rust-only directives such as `#![deny(unsafe_code)]` into this repo.
- Resource safety means:
  - browser media tracks must be stopped on all terminal paths;
  - object URLs must be revoked;
  - upload files must be closed;
  - raw audio bytes must not be stored in database columns;
  - graph tracing must remain disabled for raw media paths;
  - temporary/generated verification artifacts must not be committed.

### 2. Model and Prompt Discipline

- Do not invent a Gemini model version. Use the model actually present in `backend/app/services/llm_provider.py`.
- Do not claim deterministic model behavior unless temperature, prompt, model version, SDK version, and response schema are pinned and tested.
- Do not increase model scope to generic coaching, visual assessment, adaptive learning, or career prediction without explicit product and evaluation docs.
- The prompt must keep spoken user content untrusted and must forbid unsupported visual or confidence claims.
- Provider failures must surface as safe user-facing errors and must not persist learner evidence.

### 3. Persistence and Retention Boundary

- Current invariant: raw media is not intentionally persisted in database columns.
- Do not claim "zero cloud retention" or "no provider retention" unless provider/account settings are verified and documented.
- Uploaded audio may pass through HTTP multipart buffers and provider infrastructure; document this honestly.
- Transcripts and evaluations are sensitive persistent content and require ownership, retention, deletion, and export design before shared deployment.
- Generated local files from verification, builds, or manual checks must be excluded from committed source unless they are intentional documentation artifacts.

### 4. Zero-Fabrication and Strict Receipt Rule

- Never report tests, browser checks, network payloads, database counts, hashes, or command outputs that were not actually observed.
- Do not summarize in-flight background tasks as completed.
- Status claims must cite completed command receipts or explicitly say "not verified."
- If computer-use/browser control is unavailable, say so and do not pretend manual Chrome checks were completed.

### 5. Dependency and Workspace Resolution

- Run commands from explicit project paths:
  - backend tests from repository root: `python -m pytest tests/ -q`
  - frontend checks from `frontend/`: `npm run typecheck`, `npm test`, `npm run build`
- Prefer explicit working directories in automation to avoid sibling-folder collisions.
- Do not run package managers or build tools against ambiguous parent directories.

### 6. Anti-Mock, Anti-Hallucination, and Stub Disclosure

- Mocked providers are valid for offline tests, but their results must be labeled as mocked/offline.
- Never present mocked provider responses as live Gemini behavior.
- Never declare the product "ready," "production-grade," or "Play Store ready" until the documented acceptance checks pass with real artifacts.
- Any stub, fixed scenario, hardcoded demo identity, mocked evaluator, disabled profile update, or unimplemented route must be disclosed in status reports.
- Current known non-production facts:
  - live Gemini behavior is not manually verified in this workspace;
  - browser/device recording still needs manual Chrome verification;
  - authentication, ownership, migrations, deletion, retention policy, and adaptive coaching are not implemented.

### 7. Cryptographic Receipts and Hashes

- Any SHA-256 digest, request fingerprint, artifact hash, or evidence receipt cited in docs must be computed from the actual on-disk or received bytes.
- Do not paste placeholder hashes.
- Future request idempotency fingerprints must use server-side SHA-256 over canonical request data, not client-supplied hashes.

### 8. Public Surface and Secret Containment

- Never commit `.env`, API keys, raw recordings, transcripts from real users, or private provider responses.
- Frontend code must not contain Gemini keys or provider credentials.
- Public docs must distinguish implemented behavior from target architecture.
- Do not copy unrelated hackathon, sovereign-engine, Firestore, Antigravity, benchmark, or Rust-crate claims into this repository.

## PR 1 Manual Verification Gate

Phase 2 schema work must not begin until PR 1 manual acceptance is completed.

Required manual checks:

1. Create `backend/.env` from `.env.example` and set a valid backend-only Gemini key.
2. Start backend and frontend locally.
3. Open the frontend in Chrome with DevTools Network tab open.
4. Grant camera and microphone permissions.
5. Record at least five seconds and stop manually.
6. Confirm full replay, muted replay, and audio-only playback work.
7. Click `Get AI Feedback`.
8. Confirm the multipart request contains only:
   - `audio` with `Content-Type: audio/wav`
   - `duration_seconds`
9. Confirm no video field or video payload is uploaded.
10. Confirm transcript, four rubric labels, duration, and counts render with a valid key.
11. Record again and let automatic stop run at 60 seconds.
12. Confirm a single transition to review and released camera/microphone indicators.
13. Deny permissions and confirm recovery UI.
14. Stop backend, request feedback, and confirm the local recording remains reviewable and retryable.
15. Check the database after successful submissions: each successful submission has its own storage session, attempt number `1`, and no learner profile mutation.

If any item fails, update `docs/pr1-manual-verification.md` with the exact failure before continuing.

## Product North Star

Use `docs/product-thesis.md` as the product north star:

- solve one painful job first;
- show one evidence-backed priority;
- preserve privacy by keeping video local;
- make retry comparison honest;
- do not overbuild dashboards, gamification, or adaptive learning before the core loop is verified.

