# Roadmap

These nine phases supersede the earlier phase numbering. The audit is complete planning work, not an implementation phase. All deliverables below are proposed. Preserve the current stack; no shared demo before ownership isolation and privacy/input safeguards. Evaluation begins with offline regression tests in Phase 1 and rubric pilots in Phase 3; Phase 7 makes it a dedicated repeatable subsystem.

## Phase 1: correctness foundation

- Objective: make one single-attempt recording-to-feedback path truthful and testable.
- Deliverables: first PR specified in the audit; working build/types, resource-safe recorder, local video/audio-only upload, validated duration/media, aligned contracts/counts, bounded evaluation schema, honest error and unavailable states. Add offline contract/recorder regression checks to CI and reproducible development instructions.
- Dependencies: current audit findings and agreed measurement semantics. If full decoder validation requires a dependency, choose it explicitly in this later implementation phase.
- Acceptance: all first-PR acceptance criteria pass; no fake categories, byte-duration fallback, shared-history comparisons or unsupported skill updates; no automatic-stop leak. Remains isolated/local until Phase 2 ownership is ready.
- Tests: existing seven tests plus metric fixtures, malformed media/schema, mocked-provider multipart API, real persistence round-trip, frontend response rendering, timer/track cleanup, build and typecheck.
- Non-goals: new adaptation, new database model/migrations in the first PR, major UX change, live AI benchmarks or shared production release.

## Phase 2: domain/backend architecture

- Objective: make ownership, task semantics and structured evidence durable.
- Deliverables: user identity (including a secure anonymous option if selected), explicit session/attempt APIs and context, schema/repository/application boundaries, migrations, referential/uniqueness/check constraints, idempotency and atomic finalization; replace duplicate profile policy. Design deletion/retention and legacy-data repair/invalidation.
- Dependencies: stable contracts and measurement semantics from Phase 1; choose ownership and retention policy before shared access.
- Acceptance: different users cannot access or influence each other's history; same-task retries are linked explicitly; concurrent/repeated requests cannot duplicate sequence or profile updates; invalid historic counts and shared demo data are never silently attributed to a real user.
- Tests: actual SQLite and supported PostgreSQL constraints/transactions, HTTP authorization, duplicate/concurrent submission, migration upgrade/backfill, deletion and profile rebuild.
- Non-goals: chat memory, vector search, advanced learner models, microservices or automatic migration at import.

## Phase 3: evidence-grounded AI

- Objective: make qualitative judgments inspectable and reject unsupported conclusions.
- Deliverables: anchored audience/goal rubric, typed evidence references, transcript/input quality, finite scores, evaluator uncertainty and abstention, prompt/model/schema provenance, offline fixtures and initial evaluation runner.
- Dependencies: durable versioned attempt/evaluation records and supported input formats; consented or synthetic evaluation data.
- Acceptance: unsupported evidence cannot update a profile; every presented main diagnosis has validated provenance; unusable inputs have honest outcomes. Publish pilot methodology/results only after running it, including failures.
- Tests: provider mocks, range/schema and evidence validators, prompt-injection/low-quality fixtures, abstention workflow; separately budgeted stability/human-agreement pilot.
- Non-goals: treating confidence as calibrated without evidence, technical fact-checking guarantees, model fine-tuning, RAG or visual inference.

## Phase 4: adaptive coaching loop

- Objective: close the loop around one supported target.
- Deliverables: conditional validate/measure/evaluate/evidence/diagnose/intervene/compare/update workflow; one persisted target and actionable exercise; comparable retry outcomes; eligibility-gated interpretable profile updates; adapt an exercise when the target does not improve.
- Dependencies: Phases 2–3 ownership, provenance and reliable outcome signals.
- Acceptance: baseline, invalid input, abstention, improved retry and non-improved retry routes are distinguishable; comparison uses the assigned target; repeated processing is idempotent; insufficient evidence does not masquerade as progress.
- Tests: compiled graph scenarios with fake providers, target tie-breaks, incompatible contexts, profile gating/rebuild and baseline-to-retry API integration.
- Non-goals: multiple agents, reinforcement learning, elaborate cognitive diagnosis or claiming causal intervention effects without a study.

## Phase 5: product UX

- Objective: make evidence and the next practice action understandable.
- Deliverables: focused scenario/audience/goal setup, supported durations, deliberate full/presence/voice review, one coaching target, evidence viewer, understandable retry comparison, honest history and uncertainty; accessible failure/recovery states and consistent naming.
- Dependencies: stable explicit task APIs and tested coaching outcomes. Capture safety fixes remain Phase 1 work.
- Acceptance: users can complete the central loop and explain what to practice and why; review video remains local; unsupported scores never appear; supported browsers and accessibility checks are documented.
- Tests: frontend component and browser E2E paths, keyboard/screen-reader smoke, permissions/format handling, task preservation, formative user comprehension sessions.
- Non-goals: generic dashboard score proliferation, community features, cosmetic redesign before correctness or automated presence scoring.

## Phase 6: ML/research experimentation

- Objective: determine whether a learner-state model improves decisions beyond simple baselines.
- Deliverables: explicit research questions; compare simple averages, EMA and only then uncertainty-aware/Bayesian or state-space estimates if warranted; speaker/task splits, leakage controls, sensitivity analysis and versioned experiment reports.
- Dependencies: sufficient consented longitudinal data, credible evaluation signal, baseline system and measurable decision objective. Phase may remain deferred if data are insufficient; do not manufacture training data evidence.
- Acceptance: choose the simplest approach meeting observed needs; a more complex model is adopted only with reproducible held-out benefit relevant to future-target selection or skill estimation, including uncertainty and operational cost.
- Tests: estimator unit/rebuild tests, synthetic known-state sanity checks, held-out comparison, ablation and missing-data/correlated-retry analysis.
- Non-goals: PyTorch, fine-tuning, RL, neural diagnosis or additional infrastructure for portfolio appearance. No mandatory model upgrade.

## Phase 7: evaluation system

- Objective: make AI reliability and intervention effectiveness testable through reproducible experiments rather than claims.
- Deliverables: versioned consented/synthetic corpus; anchored rubric and annotation guide; speaker/task-separated holdout; offline regressions; explicitly budgeted live runner; schema validity, repeated-run stability, human agreement, evidence support, abstention, intervention relevance, latency and cost reports with prompt/model versions.
- Dependencies: Phase 3 evidence/quality contracts and pilot methodology, Phase 4 target/comparison semantics; Phase 6 complexity is optional and can remain deferred. Any research adoption already requires evaluation before this phase is complete.
- Acceptance: another reviewer can reproduce offline results; live runs record budget/configuration and actual usage; reports include sample size, denominators, failures, uncertainty and human disagreement. Quality thresholds are chosen from pilot evidence before holdout testing. No fabricated result or confidence-calibration claim. Normal CI makes no paid model calls.
- Tests: corpus/schema validators, evidence-reference checks, frozen output regressions, abstention cases, repeated-run and human-agreement experiments, paired prompt/model comparisons and cost/latency accounting including retries.
- Non-goals: automatic production prompt/code rewriting, training on holdout, replacing human evaluation with model self-ratings, or proving causal learning from simple score deltas.

## Phase 8: production engineering

- Objective: make the validated application operable, private and recoverable before a real-user beta.
- Deliverables: one supported deployment path, managed durable database, release migrations, reproducible dependency/runtime setup, health/readiness, bounded concurrency/timeouts/rate and cost limits, redacted telemetry, secrets/config validation, backup/restore and rollback runbooks. Run a small consented beta after these gates, feeding failures into the evaluation corpus.
- Dependencies: stable ownership/domain contracts, Phase 5 usability, Phase 7 evaluation gates and retention/deletion policy; no requirement to adopt advanced ML.
- Acceptance: clean build/deploy and smoke succeed; ownership/authorization and allowed origins verified; restore and rollback rehearsed; no raw payload traces by default; deletion covers dependent evidence; failed model calls do not produce profile updates. Beta reports actual completion, error, latency/cost and evidence-quality results with limitations.
- Tests: deployment smoke, migration/rollback/restore exercises, concurrency and failure injection, auth/CORS checks, telemetry redaction, deletion/export and real-user loop verification.
- Non-goals: Kubernetes, unnecessary microservices/queues, unmeasured scaling claims, broad launch before reliability, or retaining research recordings without explicit consent.

## Phase 9: flagship release

- Objective: present an honest, reproducible engineering artifact.
- Deliverables: accurate README/demo, architecture and ADR updates, reproducible test/evaluation commands, measured results with limitations, deployment/operations guide and a focused case study explaining tradeoffs and failure corrections.
- Dependencies: accepted beta findings, known-issue review and release verification. Include deferred research decisions honestly.
- Acceptance: every headline capability maps to code and evidence; a reviewer can reproduce offline tests and understand paid experiment boundaries; demo succeeds without exposing secrets or private learner data; unresolved limitations are visible.
- Tests: clean-clone setup, full release checks, documentation/link check, demo smoke and audit of claims against current code/results.
- Non-goals: buzzword expansion, fabricated metrics, cosmetic complexity or concealing negative experimental results.
