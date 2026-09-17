# Current-state audit

> Historical baseline: findings below describe commit `5b3ada5`. The first engineering PR addresses a subset; see the [implementation status](#first-engineering-pr-status) and [current README](../README.md) before treating a baseline defect as current behavior.

Audited 2026-09-14 at commit `5b3ada5aa3f5d0538f22c0055ae8a77931826572`. This phase changes documentation only. Findings refer to that application snapshot. Severity follows the requested definition: P0 includes currently broken, incorrect, or misleading behavior; it does not imply every finding is a security emergency.

## Coverage and evidence

Read all tracked application source, tests, root/frontend READMEs, `.agents/rules/project-rules.md`, both environment examples, ignore files, CI and deployment configurations. Parsed the entire frontend lockfile (123 package entries) and inspected resolved direct dependencies and engines. Application, dependency, test, CI and deployment files match the audited commit. Results below were recorded during the audit; documentation packaging did not rerun or repair application checks. The audit findings describe the original code and README. The README is corrected in this documentation commit; application defects remain.

| Area | Inspected files |
| --- | --- |
| Browser state and boot | `frontend/App.tsx`, `frontend/index.tsx`, `frontend/index.html`, `frontend/types.ts` |
| Recording/review/results | `frontend/components/WelcomeScreen.tsx`, `RecordingScreen.tsx`, `ReviewScreen.tsx`, `FeedbackScreen.tsx`, `Loader.tsx` |
| Transport | `frontend/services/api.ts`, `backend/app/main.py` |
| Workflow | `backend/app/agent/{state,nodes,graph}.py` |
| Domain and provider | `backend/app/domain/{metrics,evaluation,comparison,skill_profile}.py`, `backend/app/services/llm_provider.py` |
| Persistence | `backend/app/models/database.py` |
| Delivery | `backend/api/index.py`, both `vercel.json` files, `.github/workflows/ci.yml`, dependency manifests/lockfile, Vite/TypeScript/PostCSS/Tailwind configs, CSS |
| Supporting material | Both READMEs, `frontend/metadata.json`, both `.env.example` files, both ignore files, project rules, both test files |

### Executed checks

Local environment: Python 3.14.4, Node 26.4.0, npm 11.17.0. These differ from CI's Python 3.10 and Node 20.x; local results are not CI results.

- `python -m pytest tests/ -q -p no:cacheprovider`: **7 passed**, one google-genai deprecation warning. Five tests exercise database URL configuration with mocked engine/base; two exercise individual workflow nodes. No paid calls.
- `npm ci --ignore-scripts --no-audit --no-fund --offline`: succeeded from cache without manifest/lock changes.
- `npm run build`: initially blocked by sandbox directory access. Re-running outside that sandbox reached the actual build and failed because Tailwind 4 is registered directly as the PostCSS plugin.
- `node node_modules/typescript/bin/tsc --noEmit`: failed with `TS2503` for `JSX` in `FeedbackScreen.tsx:41` and `TS2339` for `ImportMeta.env` in `services/api.ts:8`.
- An isolated Python process used in-memory SQLite, disabled tracing, mocked only the evaluator, and invoked the actual async route function twice. This exercised graph routing, metrics, response construction, and real SQLAlchemy persistence, but **not HTTP/multipart transport**. Two fillers then one filler persisted as zero both times; comparison said one more filler; profile count became two while structure average remained zero. Invalid media bytes reached the mocked evaluator.
- Direct schema probe accepted `clarity=999`, `structure=-4`, `confidence=999`, and an empty transcript. A JavaScript reproduction of the frontend's array spreads against the actual response shape raised `TypeError: x.bodyLanguage is not iterable`.

No live model call, real camera/browser exercise, deployed endpoint check, production database access, human evaluation, latency benchmark, or cost experiment was performed. Recorder lifecycle findings are source-level diagnoses; build, type, metric/schema, and isolated route findings above are reproduced. No external URLs in the README were verified.

## Current system and end-to-end trace

1. `App.tsx` holds a five-state in-memory UI: welcome → recording → review → analyzing → feedback. Restart clears local feedback/blob and returns to welcome. No session context, audience, topic, goal, or history is captured.
2. `RecordingScreen.tsx` asks for camera and microphone together. A `MediaRecorder` records both tracks, and the result is labeled `video/webm` regardless of the recorder's actual format. A countdown claims to stop after 60 seconds.
3. `ReviewScreen.tsx` creates a local object URL for full replay, muted replay, or audio-only playback. It revokes the URL on unmount. Reviewing all three perspectives is optional.
4. `analyzeVideo` posts the **whole audiovisual blob** as multipart field `audio` to `/api/sessions/latest/attempts`. There is no duration, identity, or task context in the request. Response JSON is asserted to be `AIFeedback`, not runtime validated.
5. FastAPI creates/loads `demo_user` and `demo_session`, with a fixed scenario about explaining a technical project to a nontechnical person. It loads all prior attempts in that shared session and chooses the newest. It guesses duration from byte length with a five-second minimum.
6. LangGraph calls Gemini 2.5 Flash once for transcription and qualitative evaluation, calculates transcript metrics next, and conditionally compares when a previous attempt exists. Evaluation precedes measurements because it produces the transcript. The graph has no evidence-validation or learner-update node.
7. The provider requests JSON constrained by a Pydantic model and reparses it. The prompt requests four 0–10 rubric scores but does not define the separate required `confidence` field. The first model-suggested focus becomes a templated instruction.
8. The route saves an attempt and updates only average clarity and a counter named `total_sessions`. Database tables are created during module import. No saved profile is used by the evaluator or intervention selector.
9. The response maps clarity to a percentage, audience awareness to “Engagement,” and ambiguous confidence to “Confidence.” It returns transcript and comparison, which frontend types/rendering omit. Feedback rendering spreads missing category arrays and fails before a successful result can be shown.

## What exists and should be preserved

- Small, understandable React application with distinct recording, review, and feedback components. Review modes are useful reflection affordances; preserve their separation from automated assessment.
- Pure metric and comparison functions that can be tested cheaply. Preserve deterministic ownership while correcting inputs and contracts.
- A provider module isolated from routes and a structured Pydantic evaluation boundary. Extend validation rather than replace the stack.
- A small LangGraph with a real baseline/retry branch. Preserve this testable seam; do not inflate it into multiple agents.
- SQLAlchemy with SQLite fallback, legacy PostgreSQL URL normalization, and PostgreSQL connection liveness checks. Preserve portability, but it is not yet proof of hosted reliability.
- Separate frontend/backend CI jobs and a frontend lockfile. Existing tests are useful starting cases, not coverage of the product loop.
- Backend-only provider calls: no tracked frontend model secret. Object URL cleanup and absence of deliberate raw-recording database storage are useful foundations with the limitations below.

## What is still prototype-level

The recording/review UI and backend computation/persistence paths exist, but their integration is broken. The seven tests establish only two node examples and five database-configuration cases. The graph makes one model call and branches for a retry; it does not validate evidence, diagnose a highest-impact weakness, or adapt from stored learner history. The database is a schema prototype without migrations or ownership. Deployment files are configuration artifacts, not proof of a working deployed service. This is not yet a reliable closed-loop training system.

The claim ledger preserves the original README claims and their code-level contradictions. The packaged README removes those claims; UI copy and application behavior remain unchanged.

## P0: current correctness and trust failures

| ID | Finding and exact affected files | Consequence and correction |
| --- | --- | --- |
| P0-01 | `backend/app/main.py:127-132` returns only `content`; `frontend/types.ts:21-29` requires three categories; `frontend/components/FeedbackScreen.tsx:69-70` spreads all three; `frontend/services/api.ts` casts unchecked JSON | Successful feedback crashes rendering. Define an honest response contract and remove unsupported body-language/vocal categories rather than invent data. Validate the API response and test rendering with the real shape. |
| P0-02 | `backend/app/main.py:33-35` hard-codes user/session; its previous-attempt lookup and profile update use those IDs | All callers contaminate the same learner state and comparisons. Add server-owned identity and explicit session ownership before any shared deployment; random client IDs alone are not authorization. |
| P0-03 | `backend/app/main.py:70` calculates `max(bytes/20000,5)`; `RecordingScreen.tsx` records video | Byte length varies with video, codecs and bitrates; WPM and pacing conclusions are not defensible. Use a defensible duration source with explicit provenance and server-side validation; client elapsed time must not be labeled server-measured audio duration. Missing/unreliable duration must yield unavailable measurements, not a fabricated fallback. |
| P0-04 | `domain/metrics.py` emits `total_fillers`; `main.py:104` reads `filler_words_count`; `main.py:60` loads that name; `domain/comparison.py:8` expects `total_fillers` | Counts persist as zero and retries compare against a zero baseline. Map one typed measurement contract through write/read/compare. Existing historical counts require explicit repair from retained transcripts or invalidation, never silent trust. |
| P0-05 | `frontend/components/RecordingScreen.tsx:35-43,64-83` captures initial `stream=null` in cleanup and `isRecording=false` in the countdown's stop closure | Automatic stop cannot pass its guard; cleanup misses acquired tracks. Interval cleanup is absent on unmount, and async acquisition can outlive the component. Fix resource ownership using refs/recorder state; cover StrictMode and delayed permissions. Manual stop uses a later render and is a separate path. |
| P0-06 | `frontend/services/api.ts`, `RecordingScreen.tsx`, `backend/app/main.py`, `services/llm_provider.py`, `README.md` | Full video is sent to Gemini despite audio-only framing. An audio-only prompt does not strip video. Keep video local, upload a supported audio track, validate media, and disclose external processing and transcript retention. Default tracing is enabled in both env examples; assess graph-input capture before claiming no recording logs. Actual external retention was not tested. |
| P0-07 | `backend/app/domain/evaluation.py`, `services/llm_provider.py`, `main.py:124-139`, `frontend/components/{FeedbackScreen,Loader}.tsx` | Scores accept arbitrary ranges; confidence has no defined scale/meaning; audience adaptation is mislabeled engagement; loader claims posture analysis. No evidence validation precedes profile mutation. Define finite bounded judgments, separate evaluator uncertainty, remove unsupported claims, and gate updates. Pace ≥120 is always “Good pace,” even when extreme. |
| P0-08 | `frontend/package.json`, `frontend/package-lock.json`, `frontend/postcss.config.js`, `frontend/index.css` | Tailwind 4 with the old direct PostCSS registration breaks the production build. Reconcile the existing styling pipeline with minimal change, preserve appearance, then run the full build. TypeScript errors additionally involve `frontend/tsconfig.json`, `frontend/components/FeedbackScreen.tsx`, `frontend/services/api.ts`, and missing React/Vite type declarations. |

## P1: foundations blocking reliable development and operation

| ID | Affected files | Problem and correction |
| --- | --- | --- |
| P1-01 | `backend/app/main.py`, `backend/app/models/database.py` | No foreign keys, non-null/check constraints, unique session-attempt pair, timestamps, ownership enforcement, idempotency, or atomic sequence allocation. Concurrent attempts can duplicate numbers and lose aggregate updates. Use transactions and database constraints, with a migration/backfill plan. Import-time `create_all` cannot evolve deployed schemas. |
| P1-02 | `backend/app/main.py`, `backend/app/domain/skill_profile.py` | Route increments sessions per attempt and updates clarity only. Unused updater changes more fields with different logic; set truncation is not recurrence ranking. Replace duplicate policy with one evidence-based update service; distinguish session and attempt counts. No profile update is currently conditioned on reliable input. |
| P1-03 | `backend/app/main.py`, `backend/app/services/llm_provider.py`, `frontend/services/api.ts` | Unbounded reads and unvalidated MIME/media; no application duration/size limits, rate/budget controls, explicit timeout/retry policy, cancellation, or stable error model. Sync DB/provider/graph work blocks the async handler. Use bounded upload/media checks, typed errors and bounded execution; do not add a queue before measuring need. SDK behavior is not a declared application policy. |
| P1-04 | `backend/app/agent/{state,nodes,graph}.py`, `backend/app/domain/{evaluation,metrics,comparison}.py` | Broad dict state, no transcript reliability, no silence/unsupported-language route, no evidence spans, no provenance or abstention. Empty audio skips evaluation then metrics may receive `None`. Comparison is speed/count prose, not targeted improvement; its first-attempt message is not used by the first-attempt graph path. Introduce typed outcomes and quality gates. |
| P1-05 | `backend/app/models/database.py`, `backend/app/main.py`, both `.env.example` files | Transcripts persist with no retention/deletion/consent flow. No authentication; wildcard CORS with credentials is inappropriate as a default. CORS is not authorization. Configure allowed origins, ownership, retention and redacted tracing before a beta. Examples omit `DATABASE_URL`, `CORS_ORIGINS`, and frontend API URL guidance. `PORT`/`ENVIRONMENT` are not consumed by application logic. |
| P1-06 | `tests/test_workflow.py`, `tests/test_database.py`, `.github/workflows/ci.yml`, `frontend/package.json` | No actual compiled graph/provider mock test, HTTP integration, real DB lifecycle test, frontend render/recording test, browser E2E, typecheck CI step, or AI regression suite. Database mocking hides constraints and writes. Add contracts and isolated cross-layer tests first; keep CI model-free. |
| P1-07 | `backend/requirements.txt`, `.github/workflows/ci.yml`, `backend/vercel.json`, `backend/api/index.py`, `frontend/vercel.json`, `README.md` | Python dependencies are unpinned; no Python lock or test manifest. Render/Railway are prose only, alongside a different Vercel backend path. SQLite default and import-time schema creation do not establish durable cloud persistence or safe worker startup. No migration release step, readiness, backup/restore verification, rollback or deployed smoke test. Document and later test one supported deployment target. |
| P1-08 | `frontend/App.tsx`, `types.ts`, `components/FeedbackScreen.tsx`, `backend/app/main.py`, `agent/nodes.py` | Hidden fixed scenario, no explicit retry identity, returned comparison/transcript omitted in UI, focus is merely first suggestion, exercise repeats its name, no history retrieval or saved learner context supplied to AI. Preserve task context, persist a specific intervention, and compare its declared target before claiming adaptation. |

## P2: worthwhile after correctness

- `backend/app/domain/metrics.py`: document tokenizer/language scope, multiword filler whitespace and lexical ambiguity (“like,” “so,” “actually” can carry meaning). Report candidate occurrences and denominators; no pause statistics are possible without aligned audio/transcript timing. Expand fixtures before refining heuristics.
- `frontend/components/{WelcomeScreen,ReviewScreen,RecordingScreen}.tsx`, `frontend/metadata.json`, `frontend/index.html`: inconsistent Aura/soft-skills/intelligence-coach naming; missing `/vite.svg`; display timer begins `00:60`; permission failure offers no recovery control. Plan accessible states, keyboard/screen-reader feedback, browser format negotiation and duration choices without redesigning the product now.
- `frontend/vite.config.ts`: unused `loadEnv` result and empty `define`; `backend/app/main.py` has unused schema/typing imports. Remove leftovers when touching these paths.
- `backend/requirements.txt`: no direct `langchain` or `langsmith` import in application code. Review dependency purpose; retain LangSmith only for explicit privacy-reviewed instrumentation, and do not remove transitive dependencies blindly. `gunicorn` belongs to a chosen deployment path; `psycopg2-binary` supports intended PostgreSQL. No reason to replace React, FastAPI, LangGraph, Gemini, or SQLAlchemy.
- `frontend/README.md`: generated AI Studio instructions point users to a frontend Gemini key even though provider access is backend-only. Replace stale scaffold documentation. Existing root badge specifies React 19.1.1 while lock resolves 19.2.8; plugin-react requires Node >=20.19 in the 20 series, contrary to the broad Node 18+ instructions.

## Original claim ledger

README claims below refer to the audited base commit, not the corrected README included with these documents.

| Claim/location | Actual implementation | Needed correction |
| --- | --- | --- |
| README: “30-Second Use Case” including a 60-second recording and seconds-long evaluation | No timing experiment; timeline cannot contain that recording | Remove timing promises; describe ordered steps |
| README: transcript validation and mocked AI routing tests | No transcript gate; two individual-node tests, no provider mock in committed tests | Describe exact coverage and planned tests |
| README: highest-impact target and targeted exercise | First free-text focus; string template | Label as a suggested focus until evidence-based diagnosis exists |
| README: persistent evidence-based progress / agentic adaptation | Only clarity average and count update, no history fed into evaluation | Call it prototype persistence; reserve adaptive claims for verified closed-loop behavior |
| README: native audio duration and high-confidence feedback | Byte heuristic, model transcript, no confidence calibration | Qualify measurements and remove reliability guarantees |
| README: audio-only scope, ephemeral unlogged audio, delimited untrusted transcripts | Video upload; no explicit raw-media DB column, but tracing enabled by example; transcript generated by model rather than delimited input | Describe actual payload and external boundary; do not claim tracing/provider retention has been verified |
| UI loader/metadata: posture, gestures, body language, daily progress | No such scoring/history UI implemented | Delete unsupported copy and scoring categories; keep muted self-review |
| UI: Confidence and Engagement | Ambiguous evaluator field and renamed audience-awareness score | Use rubric labels actually evaluated; no speaker-confidence inference |
| README: deployment ready and graceful errors | Build fails, typecheck fails, no stable backend error envelope or deployed verification | State prototype status and publish validated setup steps later |

## Recommended corrections and first implementation PR

Only proposed first PR: **Restore a truthful single-attempt recording-to-feedback path.**

Proposed branch: `codex/trustworthy-attempt-foundation` (not created).

Exact objective: a supported local recording produces one validated, honestly labeled response whose displayed measurements agree with saved data, while invalid input or provider failure cannot create successful feedback or a skill update. This is a bounded correctness slice, not the full domain redesign. Until identity isolation lands, use only isolated local development; this PR alone does not make shared deployment acceptable.

Scope: repair build/types; fix recorder stop/cleanup and upload audio only while preserving local video review; accept bounded, validated media and trustworthy duration; align typed metric/evaluation/response contracts; remove unsupported categories/confidence/engagement/posture claims; map counts correctly; present unavailable/error states instead of fabricated values. Suspend unsupported durable skill updates until eligibility policy exists. Keep the existing layout and stack. No new adaptive feature, schema migration, or historical comparison claim is needed to complete this PR.

### Exact planned file scope

Modify these existing files:

- `frontend/components/RecordingScreen.tsx`, `frontend/components/FeedbackScreen.tsx`, `frontend/components/Loader.tsx`, `frontend/App.tsx`, `frontend/services/api.ts`, `frontend/types.ts`, `frontend/metadata.json`.
- `frontend/package.json`, `frontend/package-lock.json`, `frontend/postcss.config.js`, `frontend/index.css`, `frontend/tsconfig.json`.
- `backend/app/main.py`, `backend/app/domain/metrics.py`, `backend/app/domain/evaluation.py`, `backend/app/domain/comparison.py`, `backend/app/agent/state.py`, `backend/app/agent/nodes.py`, `backend/app/agent/graph.py`, `backend/app/services/llm_provider.py`, `backend/requirements.txt` (only if required for selected media validation; test dependencies belong in the proposed test manifest).
- `tests/test_workflow.py`, `.github/workflows/ci.yml`, `README.md`, `frontend/README.md`, `docs/current-state-audit.md`.

Add these files: `frontend/vite-env.d.ts`, `backend/app/schemas/attempt.py`, `backend/app/services/media.py`, `tests/test_attempt_api.py`, `tests/test_metrics.py`, `tests/test_evaluation.py`, `frontend/components/RecordingScreen.test.tsx`, `frontend/components/FeedbackScreen.test.tsx`, `frontend/vitest.config.ts`, `frontend/test/setup.ts`, `tests/conftest.py`, and `backend/requirements-dev.txt`. No database model or migration change is included. These paths are a proposal, not files created during this audit.

### Expected behavior

The existing welcome/record/review/feedback layout remains. Capture owns its resources and produces local video for self-review plus supported audio for upload. Use a monotonic recording-lifecycle duration or reliable media metadata with explicit provenance and server-side bounds validation. Client-reported timing is not independently verified audio duration. Do not add ffmpeg/ffprobe infrastructure for this PR. Reject unavailable/invalid duration rather than guess from bytes. An invalid provider result yields a safe, recoverable error. Valid results use actual rubric labels, explicitly qualify transcript-derived filler candidates, and retain consistent counts through persistence.

The PR must not present a previous attempt from the shared demo session as the current user's history. Until owned sessions and legacy-data eligibility exist, suppress live historical comparison and long-term profile updates; retain unit-level comparison logic for future integration. No old data are deleted or silently repaired. This removes misleading behavior without pretending identity isolation has been solved. Restrict use to isolated local development; audio-only transport alone does not complete provider/tracing privacy controls.

### Tests to add

- `tests/test_attempt_api.py`: actual multipart HTTP requests with an isolated real database and fake provider; response schema, invalid/empty/oversized/unsupported media, duration rejection, provider failure, round-trip counts, and no profile mutation or shared-history comparison.
- `tests/test_metrics.py`: known-duration fixtures, byte-size invariance, invalid/nonfinite duration, tokenizer/count cases, and two-fillers-to-one comparison against correctly mapped saved values.
- `tests/test_evaluation.py`: finite 0–10 score boundaries, missing/empty required data, malformed provider output, and undefined confidence semantics removed from the public contract.
- `tests/test_workflow.py`: compiled graph with a mocked evaluator; valid first attempt and failure paths, no successful output after invalid evaluation.
- `frontend/components/RecordingScreen.test.tsx`: manual/timed stop, exactly-one completion, unmount, delayed permissions and StrictMode cleanup; only audio in the analysis payload.
- `frontend/components/FeedbackScreen.test.tsx`: render the actual API contract, unavailable/error states and absence of unsupported categories. Exercise runtime API parsing through these fixtures rather than only TypeScript casts.
- CI: run backend tests, frontend tests, TypeScript and production build without model credentials; no live calls or production database.

### Acceptance criteria

1. Clean locked frontend install, production build, and TypeScript check succeed; visual structure is preserved.
2. Manual/automatic stop produce exactly one completed recording; every acquired track and interval is released on unmount, failure and delayed permission resolution, including StrictMode.
3. Only validated audio crosses the API/provider boundary; video stays local. Invalid/empty/oversized/unsupported input does not call Gemini. Duration has a documented measurement source and fixture-based tolerance; invalid duration never yields plausible WPM.
4. A mocked-provider HTTP response renders without exceptions and shows only supported rubric/metric fields; schema rejects nonfinite/out-of-range judgments and invalid required data. Provider failure returns a recoverable error without partial success or learner update.
5. Valid measurement counts survive persistence and mapped comparison fixtures have the correct direction. Live shared-demo comparisons and profile updates are suppressed pending ownership and evidence eligibility. Legacy counts are unverified; old rows remain intact. No unsupported improvement or skill-state claim remains visible.
6. Normal CI has no model credentials, live calls, or shared database dependency. Existing seven tests still pass alongside metric, schema, API, rendering, resource-cleanup, and contract regression tests.

### Explicit non-goals

No authentication/session redesign, database migration or historical backfill; no new task selectors, duration options, history UI, targeted intervention engine or learner model; no evidence-span framework or paid benchmark in this PR; no major UI redesign, stack replacement or deployment. No RAG, vector database, MCP, multi-agent system, fine-tuning, computer-vision scoring, RL or PyTorch.

This one PR does not resolve all P0s. Owned user/session isolation, concurrency/idempotency, durable constraints, evidence eligibility and full privacy controls remain release blockers assigned in the [roadmap](roadmap.md). Do not interpret a corrected local demonstration as production readiness. The proposed [target architecture](target-architecture.md) is the longer-term destination, not additional first-PR scope.

Delete rather than expand: unsupported feedback categories and loader claims, fabricated fallback scores/dead response branches, byte-duration heuristic, duplicate unused profile updater after policy consolidation, stale frontend setup instructions, and empty/unused config/import scaffolding. Preserve self-review, pure functions, provider isolation, graph seam, and SQLAlchemy. Do not delete old user data as a cleanup shortcut.

## First engineering PR status

Implemented on `codex/trustworthy-attempt-foundation`, based on the Phase 0 documentation commit. This is an isolated attempt path, not Phase 2 or adaptive learning.

- Fixed capture lifecycle, separate audio recording and local Three-Lens Review. Browser decoding produces mono PCM16 WAV; the server validates sample data and derives duration without ffmpeg or byte-size guessing.
- Added explicit request/success/error schemas and frontend runtime validation; removed unsupported confidence/engagement/visual categories and fabricated fallback scores.
- Persisted the response-critical measurement contract (`word_count`, `duration_seconds`, `duration_source`, `wpm`, total filler count and filler details) and verified reconstruction from a committed row in a new session.
- Removed shared-history lookup, retry comparisons and profile mutation from the live path. Deleted the unused duplicate profile updater. Each upload gets a storage session without an authenticated owner; that is isolation of processing, not an identity system.
- Added safe validation/provider/storage errors, disabled raw graph tracing on the request path, repaired the Tailwind adapter/type declarations and added offline CI gates.

Verification at this audit checkpoint: 78 backend tests and 21 frontend tests passed locally; TypeScript and production build passed. One Google SDK deprecation warning appeared on Python 3.14.4. Later CI hardening and current verification status are documented in the root README. No live Gemini, real camera/codec matrix, deployed-system or model-quality experiment was performed during this audit. See the [manual verification steps](../README.md#manual-verification) and [known limitations](../README.md#limits-and-privacy).

The graph is intentionally linear in this PR. Evidence validation, ownership, full migration tooling, idempotency, long-term skill state, target-outcome comparison and production transport limits remain future work. The historical tables and original claim ledger above are retained as audit evidence, not overwritten to hide defects. A narrow startup schema-compatibility check adds missing measurement columns for existing local databases; it is not a full migration framework.

### Implementation file manifest

Paths below list changes relative to the documentation commit. Deletions are identified explicitly.
- [.env.example](../.env.example)
- [.github/workflows/ci.yml](../.github/workflows/ci.yml)
- [README.md](../README.md)
- [backend/.env.example](../backend/.env.example)
- [backend/app/agent/graph.py](../backend/app/agent/graph.py)
- [backend/app/agent/nodes.py](../backend/app/agent/nodes.py)
- [backend/app/agent/state.py](../backend/app/agent/state.py)
- [backend/app/domain/evaluation.py](../backend/app/domain/evaluation.py)
- [backend/app/domain/metrics.py](../backend/app/domain/metrics.py)
- `backend/app/domain/skill_profile.py` — removed duplicate, unused profile updater.
- [backend/app/main.py](../backend/app/main.py)
- [backend/app/schemas/attempt.py](../backend/app/schemas/attempt.py)
- [backend/app/services/llm_provider.py](../backend/app/services/llm_provider.py)
- [backend/app/services/media.py](../backend/app/services/media.py)
- [backend/requirements-dev.txt](../backend/requirements-dev.txt)
- [docs/current-state-audit.md](../docs/current-state-audit.md)
- [frontend/App.tsx](../frontend/App.tsx)
- [frontend/README.md](../frontend/README.md)
- [frontend/components/FeedbackScreen.test.tsx](../frontend/components/FeedbackScreen.test.tsx)
- [frontend/components/FeedbackScreen.tsx](../frontend/components/FeedbackScreen.tsx)
- [frontend/components/Loader.tsx](../frontend/components/Loader.tsx)
- [frontend/components/RecordingScreen.test.tsx](../frontend/components/RecordingScreen.test.tsx)
- [frontend/components/RecordingScreen.tsx](../frontend/components/RecordingScreen.tsx)
- [frontend/components/ReviewScreen.tsx](../frontend/components/ReviewScreen.tsx)
- [frontend/components/WelcomeScreen.tsx](../frontend/components/WelcomeScreen.tsx)
- [frontend/index.css](../frontend/index.css)
- [frontend/metadata.json](../frontend/metadata.json)
- [frontend/package-lock.json](../frontend/package-lock.json)
- [frontend/package.json](../frontend/package.json)
- [frontend/postcss.config.js](../frontend/postcss.config.js)
- [frontend/services/api.test.ts](../frontend/services/api.test.ts)
- [frontend/services/api.ts](../frontend/services/api.ts)
- [frontend/services/audio.test.ts](../frontend/services/audio.test.ts)
- [frontend/services/audio.ts](../frontend/services/audio.ts)
- [frontend/services/recording.test.ts](../frontend/services/recording.test.ts)
- [frontend/services/recording.ts](../frontend/services/recording.ts)
- [frontend/test/setup.ts](../frontend/test/setup.ts)
- [frontend/types.ts](../frontend/types.ts)
- [frontend/vite-env.d.ts](../frontend/vite-env.d.ts)
- [frontend/vitest.config.ts](../frontend/vitest.config.ts)
- [tests/conftest.py](../tests/conftest.py)
- [tests/fixtures/attempt-response.json](../tests/fixtures/attempt-response.json)
- [tests/test_attempt_api.py](../tests/test_attempt_api.py)
- [tests/test_evaluation.py](../tests/test_evaluation.py)
- [tests/test_metrics.py](../tests/test_metrics.py)
- [tests/test_workflow.py](../tests/test_workflow.py)
