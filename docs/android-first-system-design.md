# Android-first system design

Status: target direction, not implemented Android client. The current React web app remains the proof that capture, audio-only upload, Gemini evaluation and retry comparison can work. The flagship product direction is an Android app for Google Play.

## Product constraint

Do not broaden the product. The first Android app solves one painful job:

> Help a technical person practice a one-minute project explanation, get one trustworthy improvement target, retry the same explanation and see whether the target moved.

This focus is what makes the app stronger for a resume, scholarship review and recruiter demo. A broad "AI speaking coach" would look generic; a narrow technical-explanation coach shows product judgment.

## Stack decision

Recommended first Android path: **React Native with TypeScript**.

Rationale:

- The existing frontend already uses React and TypeScript, so product surfaces, validation patterns and API contracts can move faster.
- The AI/backend complexity lives in Python/FastAPI, not in the client. The Android client should be excellent at capture, review, offline-safe state and trust-building UX.
- React Native is enough for the first Play Store target if media capture and playback pass device testing.
- Native Kotlin modules can be added only if React Native media reliability, background behavior or performance becomes the bottleneck.

Rejected for now:

- Native Kotlin first: stronger Android purity, but slower transition from the current React prototype.
- Flutter first: strong UI path, but it discards more current React/TypeScript work.
- WebView wrapper: fastest, but weakest signal for Android engineering and media/privacy trust.

## Android architecture

Use clean feature boundaries, even if the first app is small:

```text
android-app/
  src/
    app/                  # navigation, providers, app shell
    features/practice/    # record, review, feedback, retry comparison
    features/history/     # later: owned sessions and evidence history
    shared/api/           # typed FastAPI client and response validation
    shared/media/         # audio/video capture, encoding, playback lifecycle
    shared/design/        # tokens, components, empty/error/loading states
    shared/observability/ # redacted analytics, crash reports, performance spans
```

Data flow:

```text
User action
  -> screen event
  -> feature state machine
  -> media or API service
  -> validated response
  -> UI state
  -> local retry comparison
```

The app must keep video local. The backend remains the authority for media validation, deterministic metrics and model evaluation.

## Android MVP screens

1. **Onboarding trust screen**: one sentence promise, camera/mic explanation, "video stays on device" disclosure.
2. **Scenario setup**: fixed default "explain a technical project to a recruiter"; editable topic later.
3. **Record screen**: visible 60-second timer, mic/camera state, manual stop, permission recovery.
4. **Review screen**: full replay, muted presence review, audio-only voice review.
5. **Feedback screen**: four bounded rubric dimensions, one priority, one drill, transcript disclosure.
6. **Retry comparison screen**: compare the new attempt with the previous attempt in the same session.
7. **Limits screen**: what the AI can and cannot know.

No dashboard, streaks, social sharing or generic chatbot until the first loop proves useful.

## API contract direction

The Android app should consume the same backend capability, but Phase 2 should promote it from "latest demo attempt" to explicit owned resources:

```text
POST /api/practice-sessions
POST /api/practice-sessions/{session_id}/attempts
GET  /api/practice-sessions/{session_id}
GET  /api/practice-sessions/{session_id}/comparison
```

Required request metadata:

- scenario;
- audience;
- goal;
- client capture duration;
- audio file;
- idempotency key;
- client app version;
- privacy consent/version.

Required response metadata:

- attempt ID;
- prompt version;
- model ID;
- schema version;
- deterministic metrics version;
- evaluator status;
- evidence eligibility;
- retry comparison status.

## AI engineering practices

The Android app should make AI feel trustworthy by exposing system boundaries:

- Show "AI could not evaluate this" instead of defaulting to fake scores.
- Label transcript-derived measurements as dependent on transcription quality.
- Keep prompt/model/schema versions on every saved evaluation.
- Treat user speech as untrusted input; spoken prompt-injection attempts must not redirect the evaluator.
- Use structured outputs only; reject malformed output.
- Add budget and rate limits before public beta.
- Track latency, provider failures and validation failures without logging raw audio.

## Software engineering practices

Minimum release-quality bar:

- typed API contracts shared or generated from backend schema;
- strict TypeScript;
- feature-level state machines for recording/review/feedback/retry;
- unit tests for validation, reducers and comparison logic;
- device tests for permissions, recording, cleanup and playback;
- crash reporting with redacted context;
- CI for typecheck, tests and Android build;
- environment-specific config for dev/staging/prod;
- no secrets in client code;
- accessibility checks for screen reader labels, touch targets and contrast.

## Machine learning knowledge to show without overbuilding

This project should show ML literacy through evaluation discipline, not premature model training:

- Start with deterministic metrics and bounded LLM rubrics.
- Build a consented/synthetic evaluation corpus before claiming model quality.
- Measure schema validity, abstention rate, human-rubric agreement, repeated-run stability, latency and cost.
- Compare simple baselines before complex learner models.
- Use moving averages or uncertainty-aware estimates only after enough longitudinal evidence exists.
- Do not fine-tune until prompt, schema, evidence and retrieval-style approaches are proven insufficient.

## Google Play readiness notes

These are release constraints to verify again before publishing:

- As of September 16, 2026, Google Play says new apps and updates must target Android 16 / API level 36 or higher from August 31, 2026.
- Google Play requires developers to complete the Data safety form describing collection, sharing and protection of user data.
- The app will need privacy policy, account/data deletion decisions, permission rationale, release signing, internal testing and staged rollout before public release.

Official references:

- https://support.google.com/googleplay/android-developer/answer/11926878
- https://support.google.com/googleplay/android-developer/answer/10787469

## Resume-visible milestones

Build in this order:

1. Verified web vertical slice: live Gemini, audio-only upload and retry comparison.
2. Durable backend session model: owned practice sessions and linked baseline/retry attempts.
3. Evidence-grounded evaluator: prompt/model/schema versions and transcript evidence references.
4. React Native Android shell: record, review, feedback and retry flow.
5. Android hardening: permissions, crash reporting, accessibility, device tests and release build.
6. Small user pilot: measured completion, retry and trust outcomes.

Each milestone should produce a demo, test receipt and honest README update.
