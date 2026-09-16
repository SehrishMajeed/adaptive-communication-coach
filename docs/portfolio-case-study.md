# Portfolio case study

## One-line story

Adaptive Communication Coach is a privacy-aware AI practice loop for technical people who can build something but struggle to explain it clearly to a nontechnical listener.

The current implementation is a web vertical slice. The intended product surface is an Android app for Google Play.

## Why it is impressive

This project is not trying to look complex. It is trying to show judgment:

- pick one painful, common communication problem;
- protect the user's most sensitive asset, their video, by keeping it local;
- send only audio to the AI boundary;
- validate model output before the UI trusts it;
- compute measurable speech signals in deterministic code, not through model guesses;
- admit uncertainty instead of pretending every score proves improvement;
- close the first coaching loop with durable backend-owned retry comparison, evidence-grounded evaluation, coaching workflow routes and persisted interventions.

That combination is what makes it useful for a scholarship, professor review, or recruiter screen: it demonstrates product taste, AI engineering discipline, software testing, and honest technical communication.

## Reviewer read path

For a fast review, use this order:

1. `README.md` for setup, current flow, verification and limits.
2. `frontend/components/WelcomeScreen.tsx` for the focused user promise.
3. `frontend/App.tsx` for the baseline-to-retry state flow.
4. `frontend/components/FeedbackScreen.tsx` for the coaching and comparison surface.
5. `backend/app/services/llm_provider.py` for the Gemini boundary.
6. `backend/app/services/prompts.py` for versioned prompt control.
7. `backend/app/domain/metrics.py` and `backend/app/services/media.py` for deterministic measurement and media validation.
8. `tests/test_attempt_api.py`, `tests/test_evaluation.py`, and `frontend/components/FeedbackScreen.test.tsx` for proof that important claims are tested.
9. `docs/android-first-system-design.md` for the Android product architecture and release path.

## Claim-to-evidence ledger

| Claim | Evidence in repo | Current honesty boundary |
| --- | --- | --- |
| Practical AI product | FastAPI backend, React frontend, Gemini provider adapter, structured response schema | Prototype, not production-ready |
| AI engineering discipline | Versioned prompt builder, schema validation, provider timeout, mocked provider tests, automated agentic CI evaluation against golden corpus | No live reliability benchmark yet |
| Privacy-aware design | Browser records video locally and uploads a separate audio-only WAV | Manual Chrome DevTools verification still pending |
| Deterministic measurement | Duration, WPM and fillers are computed outside Gemini | Counts depend on transcript fidelity |
| Product judgment | Narrow technical-explanation wedge and one-priority feedback | Product-market fit is not proven |
| Durable coaching loop | Session-owned baseline, intervention, retry comparison and coaching workflow routes | Long-term profile updates are not implemented yet |
| Software engineering quality | 106 backend tests, 34 frontend tests, typecheck, build, CI workflow | Dependencies are not fully locked for production |
| Android-first product direction | Android system design, API evolution plan, Play Store readiness notes | Android app is not implemented yet |

## Resume bullets

Use only bullets that match the exact current repository state:

- Built a privacy-aware AI communication coach using `FastAPI`, `React`, `TypeScript`, and Gemini structured outputs, with local video review and audio-only upload.
- Implemented validated AI feedback contracts with Pydantic and frontend parsing to prevent unsupported rubric fields or malformed model output from reaching the UI.
- Added deterministic speech metrics for duration, word count, WPM and filler candidates, keeping measurable values outside the LLM.
- Designed a focused product loop for technical explanation practice: record, review, receive one target, retry and compare with durable backend-owned session history.
- Built durable practice sessions with anonymous ownership, session-scoped idempotent attempts, persisted interventions and backend-owned retry comparisons.
- Authored an Android-first system design covering React Native client architecture, media/privacy boundaries, API evolution, evaluation metrics and Play Store readiness.
- Built an automated Agentic Evaluation CI Pipeline (`evaluate_agent.py`) to benchmark LLM outputs on latency, abstention, and accuracy against a golden audio corpus without blocking traditional test suites.
- Wrote backend and frontend regression tests covering media validation, provider failures, API contract shape, recording cleanup and feedback comparison.

Do not claim production scale, personalization, durable agentic memory, Play Store launch, or verified learning outcomes yet.

## Scholarship angle

This project is strongest when presented as evidence of potential:

- It identifies a real educational and professional barrier: explaining technical work clearly.
- It shows responsible AI use: bounded output, validation, privacy boundaries and explicit limitations.
- It connects computer science fundamentals to a useful human problem: media handling, APIs, databases, typed contracts, testing and AI orchestration.
- It demonstrates maturity by separating shipped behavior from planned research and production work.

## Recruiter angle

This project should communicate:

- I can ship a working vertical slice, not only a design document.
- I can integrate LLMs safely instead of trusting raw model text.
- I can write tests around AI, media and API boundaries.
- I can reason about privacy, cost, latency and failure modes.
- I can explain technical tradeoffs clearly.

## Next credibility upgrades

The next work should make the prototype harder to dismiss:

1. Finish the Chrome DevTools manual verification checklist with a valid Gemini key.
2. Run a small consented user pilot and report actual completion, retry and trust findings.

## Demo script

1. Open the app and set the scenario, audience and goal on the setup screen.
2. Record a short technical explanation. Point out the context card stays visible.
3. Show that the video remains local for replay.
4. Open DevTools Network and verify the request uploads `audio`, `duration_seconds` and `idempotency_key`, not video.
5. Show the one suggested focus, drill, evidence quotes and trust notes.
6. Retry the same explanation within the same session.
7. Show the durable backend comparison and session history panel.
