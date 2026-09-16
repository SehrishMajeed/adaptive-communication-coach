# Engineering practices

Status: operating standard for this project. These practices define what "impressive" means: focused product behavior, verified claims and clean engineering boundaries.

## Product engineering

- Solve one painful problem before adding adjacent use cases.
- Prefer one complete loop over many incomplete screens.
- Every headline claim must map to code, tests, manual verification or a clearly labeled plan.
- Keep the UX calm and trustworthy: one target, one drill, one retry.
- Treat "Play Store app" as a release path, not a decoration.

## Software engineering

- Keep frontend, API, domain logic, provider adapter and persistence boundaries separate.
- Put deterministic logic in pure functions with tests.
- Validate external input at every boundary: browser, API, model output and database.
- Use typed contracts and reject unsupported fields instead of rendering invented UI.
- Make error states recoverable and specific.
- Use CI as the normal proof path; manual verification complements it.
- Do not add infrastructure until a concrete failure mode requires it.

## AI engineering

- Prompts are code: version them, test them and store their version with outputs.
- LLM output is untrusted: schema-validate it and fail safely.
- User speech and scenario text are untrusted: isolate them from evaluator instructions.
- Deterministic metrics stay outside the model.
- Provider timeouts, retries, cost limits and failure rates are product concerns.
- No raw media in logs, traces or durable storage unless there is explicit consent and retention policy.
- Do not claim personalization until ownership, comparable attempts and profile-safe updates exist.

## Machine learning and evaluation

- Treat the first system as AI-assisted evaluation, not a trained ML product.
- Use human-reviewed examples or synthetic fixtures before claiming quality.
- Measure rubric agreement, repeated-run stability, evidence validity and abstention behavior.
- Prefer simple interpretable baselines before complex learner-state models.
- Report uncertainty, failures and sample size honestly.
- Keep training, evaluation and demo data separated.

## Android engineering

- Android is the target product surface; the web app is the technical proof.
- Choose React Native first for speed and reuse, with native Kotlin modules only where measurement proves a need.
- Build with explicit recording states, permission recovery and media cleanup.
- Keep video local and visible as a trust feature.
- Add crash reporting, accessibility checks, staged testing and release signing before Play Store production.
- Verify current Google Play API-level, privacy and data-safety requirements before release.

## Resume standard

A reviewer should be able to see:

- why the problem matters;
- how the system works;
- where AI is used and constrained;
- what is tested;
- what is not yet proven;
- what the next system-design step is.

If a claim cannot survive that review, keep it out of the resume.
