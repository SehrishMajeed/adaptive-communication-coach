# Testing strategy

Status: active strategy. Current local evidence is 94 passing backend tests, 23 passing frontend tests, passing TypeScript checks and a passing production frontend build. Normal CI must not need model credentials or make paid calls.

## Test layers

| Layer | Required cases and assertions |
| --- | --- |
| Unit | Small pure policies, typed schema boundaries, comparable-task checks, target tie-breaking, eligibility and unavailable-value behavior |
| Deterministic metrics | Hand-counted text, punctuation, contractions, Unicode/language scope, repeated/multiword candidates, empty text, silence, invalid/zero/negative/nonfinite duration, fractional duration, very short input, rates/denominators and rounding |
| Media measurement | Committed or generated non-sensitive fixtures with known duration across supported containers/bitrates; identical content at different byte sizes must not change duration/WPM beyond declared tolerance; reject malformed or oversized media before provider calls |
| Domain logic | Same-context baseline/retry, target-specific outcome, audience changes, ambiguous improvement, unsupported evidence, duplicate observation, profile rebuild equivalence, correlated retries and deletion/supersession behavior |
| Database | Real isolated SQLite plus PostgreSQL integration for supported release path; constraints, foreign-key enforcement, commit/rollback, unique sequence/idempotency, concurrent attempts, no lost profile update, deletion and migration/backfill behavior |
| API integration | Actual multipart requests, stable response schema/status, ownership isolation, invalid media, provider timeout/invalid JSON, persistence failure, no premature success, request retry idempotency; reload saved measurements before comparison |
| Workflow | Invoke compiled graph with a fake provider; assert baseline and retry routes, unusable input, invalid evidence, abstention, target improvement/non-improvement, and exactly-once eligible finalization |
| Provider adapter | Mock SDK transport/client boundary: valid structured response, missing fields, score bounds/nonfinite values, empty output, malformed JSON, timeout/rate limit, retry exhaustion, usage metadata; no live client initialization needed in normal tests |
| Frontend | Render actual API contract fixtures; unavailable/abstained results, request error/retry, comparison visibility, task preservation; fake MediaRecorder/tracks/timers for manual and automatic stop, one completion, unmount cleanup, delayed permissions and StrictMode |
| Browser E2E | Fake media and stubbed backend for select task → record → review all modes → feedback → retry → comparison; verify audio-only upload, error recovery, accessibility basics; separate manual supported-browser media smoke test |
| AI eval/regression | Versioned consented/synthetic corpus, frozen outputs for offline checks, optional budgeted live experiments, human rubric comparison, evidence validity, input/evidence/feedback status validity, stability, prompt regressions and intervention quality |

## Critical regressions to encode first

- Backend-shaped `{content: [...]}` feedback must render without nonexistent arrays.
- Known-duration audio must not change WPM because video resolution or encoding byte size changes.
- Two fillers then one filler must survive database round-trip and report a decrease, never an increase.
- Every caller must see only owned sessions/attempts; forged session IDs must fail before retrieving a baseline.
- Confidence is never displayed as speaker confidence; unsupported visual categories never appear.
- Quality statuses must stay honest: completed feedback requires usable/non-unusable input, quote-verified evidence and actionable feedback; abstention requires non-usable-or-limited input, unavailable/insufficient evidence and no scores.
- Coaching writes must be quality-gated: abstained or limited-quality attempts may persist their result but must not create interventions, complete interventions or create retry comparisons.
- A timed-out/invalid evaluation cannot update learner state. Repeated submit/finalize cannot double-count.
- Recorder automatic stop and cleanup must work independently of stale React closures.

## Isolation and CI contract

Inject provider and database dependencies. Use temporary databases and test identities; explicitly disable tracing and network in offline suites. Do not mock the ORM base in persistence tests: the current URL-only tests can remain separately labeled configuration tests. Never point tests at a developer/production `DATABASE_URL` or send personal recordings to services.

PR CI should run locked dependency installation, backend unit/domain/API/workflow tests, frontend typecheck, render/resource tests, and production build. Add a small offline E2E smoke when the corrected vertical slice exists. Run PostgreSQL/migration integration when introducing durable schema changes and on relevant releases. Record runtime versions; match documented supported versions rather than relying only on one workstation.

Use deterministic fixtures for normal CI. A fake evaluator must exercise the real parser/contract at an appropriate layer; bypassing every boundary would repeat today's testing gap. Fake timers belong in recorder tests, not in provider latency experiments.

Live AI experiments are separate, explicitly triggered and budget capped. They may require credentials but must never be an implicit PR prerequisite. Keep corpus versions, anonymization/consent, model/prompt/schema versions, raw authorized judgments and measured results separate from test assertions. Report skipped or unrun checks explicitly. No passing claim is justified by merely adding a workflow file.

## Release gates

For the first implementation PR, require the six acceptance criteria and named checks in the audit. For a shared beta, additionally require identity isolation, transaction/concurrency tests, deletion/retention checks, deployment smoke and documented failure recovery. Thresholds for AI quality are selected using pilot data and frozen before held-out evaluation, not fabricated during implementation.
