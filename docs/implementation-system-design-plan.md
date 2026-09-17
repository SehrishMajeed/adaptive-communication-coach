# Implementation and system design plan

Status: implementation guide for the next PRs. This narrows the project to one painful problem and turns the product/AI/Android ambition into buildable system-design steps.

## North star

Build an Android-first AI practice product that helps a technical person explain one project clearly to a recruiter or nontechnical listener.

The first winning loop is:

```text
record -> review privately -> receive one target -> do one drill -> retry -> compare
```

Everything that does not improve this loop is deferred.

## What success should show

This project should make a professor, scholarship reviewer or recruiter see:

- product judgment: one real painful problem, not a generic AI wrapper;
- software engineering: typed boundaries, tests, database design, CI and release discipline;
- AI engineering: versioned prompts, schema validation, prompt-injection awareness, deterministic metrics and safe failure modes;
- ML literacy: evaluation methodology, baselines, uncertainty and measured improvement instead of fake intelligence;
- Android product thinking: Play Store path, permissions, privacy, accessibility, device testing and release staging.

## Source-aligned constraints

| Source family | Design implication |
| --- | --- |
| Google Play target API policy | Android release planning must target the current required API level; as of September 16, 2026, Google Play lists Android 16 / API 36 for new apps and updates from August 31, 2026. |
| Google Play Data safety | Any Play Store track requires accurate disclosure of collected/shared/protected data, so raw audio/video/transcript handling must be explicit before release. |
| OWASP LLM guidance | Spoken and typed user content must be treated as untrusted input; prompt injection and improper output handling are core risks. |
| NIST trustworthy AI framing | The product should demonstrate validity, reliability, safety, security, resilience, transparency and accountability through tests and documented limits. |

References:

- https://support.google.com/googleplay/android-developer/answer/11926878
- https://support.google.com/googleplay/android-developer/answer/10787469
- https://owasp.org/www-project-top-10-for-large-language-model-applications/
- https://airc.nist.gov/

## Product narrowing rules

Build only for this first scenario:

> "Explain a technical project to a recruiter or nontechnical interviewer in 60 seconds."

Do not add:

- generic public speaking categories;
- body-language scoring;
- long dashboards;
- chatbot coaching;
- streaks or gamification;
- fine-tuning;
- multi-agent personas;
- broad social/community features.

Add these only when the core loop proves useful:

- durable history;
- multiple scenarios;
- Android notifications;
- longitudinal skill profile;
- user-facing progress trends.

## Prompt and AI process

The evaluator should remain boring, bounded and testable:

1. Build prompt from a versioned function.
2. Put scenario/user content inside a clearly delimited untrusted context block.
3. Send audio and prompt to Gemini through one provider adapter.
4. Require structured output matching `CommunicationEvaluation`.
5. Reject malformed, nonfinite, unsupported or extra fields.
6. Compute duration, WPM and filler candidates in Python.
7. Save model ID, prompt version, schema version and metric version with each completed evaluation.
8. Show uncertainty and abstention before showing weak feedback.

This is more impressive than adding another model because it shows disciplined AI engineering.

## Phase 2 system design: durable practice sessions

Current gap: every backend submission creates an independent demo session. The frontend comparison is in-memory only.

Phase 2 goal:

> Make a same-session baseline and retry durable, owned and comparable.

### Entities to implement first

```text
PracticeUser
  id
  anonymous_device_id_hash
  created_at
  deleted_at

PracticeSession
  id
  owner_id
  scenario
  audience
  goal
  requested_duration_seconds
  status
  created_at
  completed_at

Attempt
  id
  session_id
  sequence_number
  idempotency_key
  status
  capture_duration_seconds
  media_duration_seconds
  transcript
  created_at
  finalized_at
  failure_code

Evaluation
  id
  attempt_id
  prompt_version
  model_id
  schema_version
  rubric_version
  evaluator_status
  clarity
  structure
  conciseness
  audience_awareness
  strengths_json
  weaknesses_json
  recommended_focus

Measurement
  id
  attempt_id
  metric_version
  duration_source
  word_count
  wpm
  total_fillers
  filler_words_json

Intervention
  id
  session_id
  source_attempt_id
  target_skill
  drill_version
  drill_text
  status

AttemptComparison
  id
  session_id
  baseline_attempt_id
  retry_attempt_id
  intervention_id
  target_skill
  comparability_status
  verdict
  deltas_json
```

### API shape

```text
POST /api/practice-sessions
POST /api/practice-sessions/{session_id}/attempts
GET  /api/practice-sessions/{session_id}
GET  /api/practice-sessions/{session_id}/comparison
```

### Phase 2 invariants

- A session has exactly one owner.
- A retry can compare only attempts from the same session.
- `(session_id, sequence_number)` is unique.
- `(session_id, idempotency_key)` is unique.
- A failed provider call cannot create a completed evaluation.
- A completed attempt stores prompt/model/schema/metric versions.
- A comparison is unavailable if the baseline and retry differ in scenario, audience, goal or rubric version.
- No profile update happens in Phase 2.

## Android-first architecture path

Do not build Android before Phase 2 starts, but design for it now.

Recommended Android path:

- React Native + TypeScript for first Play Store client.
- FastAPI backend remains source of truth for validation/evaluation.
- Local video stays on device.
- Audio upload is explicit and consented.
- API responses are runtime-validated in the client.
- Media permissions, cleanup and retry state are first-class.

First Android feature module:

```text
practice/
  setup
  record
  review
  feedback
  retry-comparison
```

## PR sequence

### PR 2A: migrations and durable schema

Deliver:

- Add Alembic.
- Add Phase 2 tables.
- Keep existing endpoint behavior working.
- Add migration tests and database constraints.

Implementation status:

- Alembic scaffolding and the first Phase 2 practice-schema migration have been added.
- The new schema is present alongside the legacy prototype tables; existing endpoint behavior remains unchanged until PR 2B.
- Migration tests verify table creation, attempt sequence uniqueness, idempotency uniqueness and selected check constraints.

Acceptance:

- Existing 79 backend tests still pass.
- New migration test proves upgrade creates tables.
- Unique constraints reject duplicate attempt sequences and idempotency keys.

### PR 2B: session APIs

Deliver:

- `POST /api/practice-sessions`.
- `POST /api/practice-sessions/{session_id}/attempts`.
- Anonymous owner token or device-scoped owner placeholder.
- Keep old endpoint only as compatibility shim or mark deprecated.

Implementation status:

- `POST /api/practice-sessions` creates an owned anonymous practice session.
- `POST /api/practice-sessions/{session_id}/attempts` evaluates and stores attempts in the Phase 2 schema.
- The legacy `/api/sessions/latest/attempts` endpoint remains available as a web-prototype compatibility shim.
- Session-scoped attempts store prompt, model, schema, rubric and metric versions.
- Tests cover ownership rejection, idempotency replay, provider failure rollback and missing-session behavior.

Acceptance:

- Attempts cannot be added to another owner's session.
- Invalid session IDs fail safely.
- Provider failure leaves an attempt failed or absent, not completed.

### PR 2C: durable comparison

Deliver:

- Persist interventions and retry comparisons.
- Return comparison from backend, not frontend memory.
- Keep frontend display honest about unavailable/insufficient evidence.

Implementation status:

- Baseline session attempts now create a persisted `PracticeIntervention` when the evaluator recommends a focus.
- Retry attempts now create a persisted `AttemptComparison` against the intervention source attempt.
- Session-scoped attempt responses include backend-owned `intervention` and `comparison` objects.
- Idempotent replay returns the existing completed attempt and saved comparison without another evaluator call.
- The React web UI now creates a practice session, submits session-scoped attempts and renders backend-owned retry comparison.

Acceptance:

- Same-session retry shows comparison.
- Different context refuses comparison.
- Repeated request does not double-create comparison.

### PR 3A: evidence-grounded evaluation

Deliver:

- Evidence references from feedback to transcript spans.
- Evaluator quality/abstention status.
- Prompt/model/schema/rubric versions in response.

Implementation status:

- `CommunicationEvaluation` now includes `evaluator_status`, `abstention_reason`, and quote-backed `evidence`.
- Completed evaluations require all scores and at least one evidence quote that appears in the transcript.
- Abstained evaluations cannot include scores, evidence or recommended focus.
- Attempt responses include prompt/model/schema/rubric/metric provenance.
- Session-scoped evaluations persist evidence and abstention reason.
- The feedback UI renders transcript evidence and provenance, and avoids fake drills when the evaluator abstains.

Acceptance:

- Unsupported feedback cannot render as confident advice.
- Prompt-injection fixture cannot alter evaluator role.
- Empty/low-quality transcript abstains.

### PR 3B: offline evaluation fixtures

Deliver:

- Add committed evaluator fixtures for normal feedback, abstention and spoken prompt-injection resistance.
- Add a local runner that validates fixtures without live provider calls.
- Document the harness and its limits.

Implementation status:

- `tests/fixtures/evaluations/` contains normal, abstention and prompt-injection fixtures.
- `backend/app/evaluation/offline_runner.py` validates fixture schema, prompt version, untrusted-speech boundary, expected status/focus and required evidence quote.
- `tests/test_offline_evaluation.py` runs the harness in CI-compatible offline mode.
- `docs/offline-evaluation.md` documents the fixture set, runner and honest limits.

Acceptance:

- Offline fixtures pass without credentials.
- Prompt-injection fixture is treated as transcript content, not evaluator instruction.
- Abstention fixture has no scores, evidence or recommended focus.
- The docs do not claim live-model quality or human agreement.

### Phase 4A: domain coaching policy

Deliver:

- Move coaching eligibility, target extraction, drill selection and comparison verdicts out of API route code.
- Keep database writes in the application route for now; do not add repository/service abstractions before they pay for themselves.
- Add direct domain tests for the policy in addition to HTTP integration tests.

Implementation status:

- `backend/app/domain/coaching.py` owns the coaching write gate, deterministic drill mapping and comparison verdict thresholds.
- `backend/app/main.py` delegates intervention/comparison decisions to the domain policy while retaining HTTP and transaction responsibilities.

Acceptance:

- Abstained or low-quality attempts persist reviewable results but cannot create coaching artifacts.
- The same policy works for provider-returned evaluations and persisted evaluation rows.
- Route tests and domain tests both prove the gate.

### Phase 4B: explicit backend workflow routes

Deliver:

- Add named attempt workflow routes for abstained, baseline, blocked baseline, missing-baseline retry, blocked retry and comparable retry.
- Route intervention/comparison writes through those named decisions.
- Keep the implementation inside the modular backend; do not add a queue, microservice or separate workflow runtime yet.

Implementation status:

- `backend/app/domain/coaching.py` exposes `AttemptWorkflowDecision` and `decide_attempt_workflow`.
- `backend/app/main.py` checks route decisions before creating interventions or comparisons.
- `tests/test_coaching_policy.py` covers baseline, abstained, comparable retry and blocked retry routes directly.

Acceptance:

- First eligible attempts establish a baseline intervention.
- Abstained attempts persist but do not create coaching artifacts.
- Eligible retries with a prior eligible intervention can compare.
- Low-quality or missing-baseline retries cannot masquerade as progress.

### Phase 4C: visible workflow route

Deliver:

- Return the selected backend workflow route in the session-scoped attempt response.
- Parse and render that route subtly in the web feedback UI.
- Keep the display factual and non-marketing: it explains the engine path, not user skill.

Implementation status:

- `PracticeAttemptResponse` includes `workflow`.
- `frontend/types.ts` validates the workflow contract.
- `FeedbackScreen` renders a compact coaching-engine note.

Acceptance:

- Baseline, abstained, retry-blocked and comparable retry responses expose honest workflow routes.
- Frontend rejects malformed workflow metadata.
- UI shows the route without implying long-term progress.

### Phase 4D: persisted workflow audit trail

Deliver:

- Persist `workflow_route` and `workflow_reason` on durable practice attempts.
- Add migration constraints so only supported workflow states can be stored.
- Replay workflow metadata from stored attempt fields instead of deriving it only at response time.

Implementation status:

- `practice_attempts` includes constrained `workflow_route` and `workflow_reason` columns.
- Session-scoped attempt finalization writes the selected route and reason.
- Idempotent replay returns stored workflow metadata.

Acceptance:

- Baseline, abstained, retry-blocked and comparable retry attempts store route and reason.
- Invalid workflow route/reason values are rejected by migration constraints.
- The response contract remains consistent with stored audit fields.

### Phase 4E: current-session attempt history

Deliver:

- Add an owner-scoped endpoint to list durable attempts for a practice session.
- Return each attempt with measurements, evaluation, workflow, intervention and comparison.
- Preserve sequence ordering and ownership isolation.

Implementation status:

- `GET /api/practice-sessions/{session_id}/attempts` returns ordered session attempts.
- The endpoint rejects wrong owners and missing sessions.
- History reconstruction reuses the same response contract as live attempt submission.

Acceptance:

- Android/web clients can reload current-session state without resubmitting audio.
- Reviewers can see durable coaching state across attempts.
- A forged owner token cannot read another session's attempt history.

### Phase 5A: web history panel

Deliver:

- Fetch current-session attempt history after each analysis.
- Render a compact durable history panel on the feedback screen.
- Keep labels honest: route, WPM, evidence status and comparison verdict only.

Implementation status:

- `fetchPracticeSessionHistory` calls the owner-scoped history endpoint.
- `FeedbackScreen` renders a lightweight `Session history` panel.
- Component and API tests cover history parsing and display.

Acceptance:

- Users can see current-session durable attempts without resubmitting audio.
- The panel does not claim long-term profile progress.
- The UI gives Android a clear reference for the retry/history experience.

### Phase 5B: explicit web setup

Deliver:

- Add scenario, audience and goal setup to the web welcome flow.
- Send setup fields when creating a practice session.
- Preserve the focused 60-second product loop without adding generic dashboards.

Implementation status:

- `WelcomeScreen` collects scenario, audience and goal.
- `analyzeRecording` passes setup into `createPracticeSession`.
- Frontend tests cover the setup form and session-create payload.

Acceptance:

- The web app no longer feels like a fixed-demo loop.
- Session context is explicit before recording.
- The setup contract matches the backend `PracticeSessionCreate` schema.

### Phase 5C: context visibility across web flow

Deliver:

- Show selected scenario, audience and goal on recording, review and feedback screens.
- Keep the context compact so it reinforces the task without becoming a dashboard.
- Preserve the same setup contract that Android will reuse.

Implementation status:

- `PracticeContextCard` renders the selected scenario, audience, goal and target duration.
- `App` passes setup through recording, review and feedback.
- Frontend tests cover context visibility across the web flow.

Acceptance:

- Users never lose sight of who they are speaking to and what outcome they are practicing.
- Reviewers can see the product is scenario-aware before the Android shell starts.
- The visible context matches the backend-owned session setup.

### PR 5D: Android shell

Deliver:

- React Native app shell.
- Practice module screens.
- Permission rationale and local replay.
- Typed API client.

Acceptance:

- Internal Android debug build works.
- Device test covers record -> review -> upload -> feedback.
- No secret or provider key exists in the client.

## Resume milestone map

| Milestone | Resume value |
| --- | --- |
| Web vertical slice | Proves full-stack AI product execution |
| Durable schema | Proves backend/system design maturity |
| Evidence-grounded evaluation | Proves serious AI engineering practice |
| Android shell | Proves Play Store product direction |
| Device testing and release pipeline | Proves production-readiness thinking |
| User pilot | Proves product validation mindset |

## Definition of "done" for the next step

Phase 6 device hardening is complete for the repository-level checks below. The release pipeline and real-device acceptance remain future release gates:

- GitHub Actions CI pipeline added for React Native testing, typechecking, linting and tests (`.github/workflows/ci.yml`).
- Accessibility props (`accessibilityRole`, `accessibilityLabel`, `accessibilityHint`) added to core navigation and interaction buttons across all Android screens.
- PII-safe observability logging boundary created at `mobile/src/shared/observability/logger.ts` for safe integration with external crash reporters like Sentry.
- Release builds no longer reuse the debug keystore; production signing requires explicit `AURACOACH_RELEASE_*` environment variables.
- Android ARM64 debug APK build is verified from a fresh short-path Windows checkout to avoid CMake path-length failures in native React Native modules.
- Real-device recording, signed release builds, Play Console setup and staged rollout are not verified.
- Real-device smoke testing is documented in `docs/android-real-device-smoke-test.md`; the first attempt was blocked because no ADB-authorized Android device was connected and no backend Gemini key was configured.

The next step is the Final Project Review and wrap-up.
