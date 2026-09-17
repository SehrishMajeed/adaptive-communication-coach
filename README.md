# Adaptive Communication Coach

[![CI](https://github.com/SehrishMajeed/adaptive-communication-coach/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/SehrishMajeed/adaptive-communication-coach/actions/workflows/ci.yml)

**Prototype — not production-ready.** Practice a technical explanation, review the recording locally, and request audio-based AI suggestions. Personalized coaching and verified improvement are not implemented.

## Portfolio positioning

This project is intentionally shaped as a practical AI engineering product: a Python/FastAPI backend, React/Vite frontend, React Native Android client, Gemini provider boundary, structured AI output validation, deterministic measurement code, privacy-aware media handling, durable practice sessions, persisted interventions, and backend-owned retry comparison. It is not yet a fully agentic product; the roadmap points toward agentic coaching once the system can autonomously choose and adapt interventions across a longer learner profile.

## Current flow

1. Record a technical project explanation for a nontechnical listener (1–60 seconds).
2. Review full video/audio, muted video, or audio-only playback. These are human self-review modes.
3. Request feedback. A separate audio recording is decoded in the browser and encoded as mono PCM16 WAV. Video stays local.
4. FastAPI validates WAV format, sample frames, size and duration, and cross-checks client monotonic capture time. Duration and WPM use decoded sample frames, not compressed file size or an LLM estimate.
5. Gemini returns a bounded structured transcript/rubric result. Python counts transcript words and filler candidates. The API atomically saves the attempt and returns a validated response; React validates it again before rendering.

The web frontend now uses explicit practice-session APIs for durable owned sessions, session-scoped attempts, persisted interventions and backend-owned retry comparisons. The legacy latest-attempt endpoint remains as a compatibility shim. Evaluations include prompt/model/schema/rubric/metric provenance and quote-backed transcript evidence; the evaluator can abstain instead of inventing feedback. Long-term profile updates are not implemented. A suggested focus is not a verified highest-impact diagnosis. Counts depend on transcript fidelity; the prototype does not independently establish speech accuracy.

See the [documentation index](docs/README.md) for the target architecture and [historical audit with implementation status](docs/current-state-audit.md). Future capabilities are explicitly separated from this working slice.

## Android-first direction

The web app served as the technical proof, but the core product surface is the newly implemented React Native Android app (`mobile/`). This application reuses the exact same API contracts and keeps the loop narrow: record a technical explanation, review privately, receive one target, retry and compare. 

The Android plan is documented in [Android-first system design](docs/android-first-system-design.md), the operating standards are in [Engineering practices](docs/engineering-practices.md), and the executed PR sequence is in [Implementation and system design plan](docs/implementation-system-design-plan.md).

## Local development

CI uses Python 3.10 and the latest stable Node 22 release. The current frontend test dependencies require a recent Node 22 release, a compatible Node 24 release (24.15+), or Node 26+. Python runtime dependencies are not locked yet.

Backend, from the repository root:

```sh
cd backend
python -m venv .venv
# Activate .venv using the command appropriate to your shell.
pip install -r requirements-dev.txt
# Copy .env.example to .env; set GEMINI_API_KEY on the backend only.
uvicorn app.main:app --reload
```

Schema migrations, from the repository root:

```sh
alembic upgrade head
```

`DB_AUTO_CREATE=true` preserves the local prototype path. Release-style environments should use Alembic migrations deliberately instead of relying on import-time table creation.

Frontend, in another terminal from the repository root:

```sh
cd frontend
npm ci
npm run dev
```

`VITE_API_BASE_URL` defaults to `http://localhost:8000`. `CORS_ORIGINS` defaults to `http://localhost:5173`; configure the actual frontend origin when needed. `DATABASE_URL` defaults to local SQLite. Use localhost or HTTPS for camera/microphone access. There are no frontend provider keys.

## Verification

From the repository root:

```sh
python -m pytest tests/
python -m backend.scripts.evaluate_agent
alembic upgrade head
cd frontend
npm run typecheck
npm test
npm run build
cd ../mobile
npm run typecheck
npm run lint
npm test
```

Local verification on Python 3.14.4 / Node 26.4.0: **108 backend tests, 34 frontend tests, and the mobile test suite pass**, and TypeScript/production builds pass. Backend tests include actual multipart HTTP requests, real isolated SQLite round-trips, Alembic migration checks, session-scoped attempt APIs, ownership checks, persisted intervention/comparison behavior, evidence validation, abstention validation, offline evaluation fixtures, coaching policy tests, compiled workflow paths with a mocked provider and live-evaluation runner safety checks. The `evaluate_agent.py` runner is a manual live Gemini evaluation entry point; without `GEMINI_API_KEY`, it writes an explicit skipped report and makes no provider call. Frontend tests cover session-scoped upload, practice context visibility, review screen modes, evidence rendering and backend-owned comparison rendering. Mobile checks cover React Native typecheck, lint and rendering/navigation boundaries. A focused Android ARM64 debug APK build is verified from a fresh short-path Windows checkout because native module CMake builds can exceed path limits under long OneDrive paths. The SDK emits one deprecation warning on Python 3.14. Deterministic automated testing occurs via GitHub Actions (`.github/workflows/ci.yml`); live provider evaluation is manual via `.github/workflows/agentic_evaluation.yml`.

## What this demonstrates

- Product development: a narrow, high-pain communication practice loop instead of a generic AI wrapper.
- AI engineering: versioned prompts, bounded Gemini output, schema validation, timeout control, safe failure behavior, offline evaluation fixtures, and a manual live Gemini evaluation gate.
- Full-stack execution: React/React Native media capture/review, FastAPI validation/persistence, GitHub Actions CI validation, and contract tests across backend, web frontend, and mobile.
- Engineering maturity: privacy boundaries, crash reporting boundaries, accessibility (a11y) roles, known limitations, ADRs, roadmap and claim-to-evidence documentation.

For a scholarship, professor or recruiter review path, see [Portfolio case study](docs/portfolio-case-study.md).

Normal CI uses mocked providers and no paid model calls. Live Gemini behavior, real-device recording compatibility, production deployment and model reliability benchmarks have not been verified.

## Manual verification

1. Start both services and open the frontend. Allow camera and microphone access.
2. Record at least five seconds; stop manually. Confirm the camera/microphone indicators turn off and all three replay modes work.
3. Choose Get AI Feedback. In browser Network tools, verify multipart fields contain only `audio` (`audio/wav`) and `duration_seconds`; no video field or video payload is uploaded. With a valid backend key, confirm transcript, four rubric labels, duration and counts render.
4. Start another recording and let it stop automatically after 60 seconds. Confirm a single transition to review and released media resources.
5. Deny permissions, then use Try Again. Stop the backend and request feedback; verify the error leaves the local recording reviewable and retryable. Restore it and retry.
6. Check the database: each successful submission has its own storage session and attempt number 1. Response-critical measurement evidence can be reconstructed from the saved attempt; learner profiles remain unchanged.

These steps are a manual checklist, not reported completed testing.

## Limits and privacy

- The browser must support camera/microphone capture, both recording formats and decoding its chosen audio format. Decode failure is recoverable and leaves local review available. Real Safari/Firefox/Chrome device coverage remains to be established.
- The analysis endpoint accepts mono PCM16 WAV only, 1–65 seconds, up to 16 MiB, with capture/sample durations within 1.5 seconds. The extra five seconds tolerate timer/codec overhead, not a new duration option. Other media is rejected before calling Gemini.
- Provider requests have a 45-second timeout with one SDK attempt; browser requests abort after 60 seconds. Session-scoped attempts use an idempotency key to prevent duplicate evaluations within the same session.
- Raw media is not saved in database columns; upload handling may spool temporary files. Graph tracing is disabled for this path and in environment examples. External provider retention is a separate, unverified boundary.
- Transcripts/results are persisted without authentication, deletion or retention policy. Storage-session UUIDs are not user ownership. Do not submit confidential material or expose this as a multi-user service.
- SQLite/PostgreSQL configuration and existing deployment files remain. Alembic migrations manage the durable schema. Global request/rate limits, durable job recovery, deployment smoke and backups are not implemented. Multipart transport limits require a production boundary; application size validation occurs after multipart parsing.
