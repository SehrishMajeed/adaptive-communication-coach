# Product and AI engineering alignment

Status: working alignment brief for product review, Lovable/Figma transfer and implementation judgment. This is not a launch claim.

## Executive story

AuraCoach is an Android-first AI practice loop for technical people who understand their work but struggle to make the explanation land for a recruiter, investor, customer or nontechnical teammate.

The product should not become a generic public-speaking app. Its strongest wedge is:

```text
I built something technical. Help me explain it clearly in 60 seconds to someone who does not share my context.
```

The app proves software engineering and AI engineering maturity by keeping the loop narrow, validating every boundary, admitting uncertainty and comparing a retry only when the context is actually comparable.

## User pain

Target users:

- CS students and early-career engineers preparing for interviews.
- AI/ML builders explaining demos, research or systems.
- Startup founders and technical operators explaining a product to investors, customers or hires.

Observed pain:

- They know the system internally, but the explanation assumes too much context.
- They ramble through implementation details before naming the user value.
- Generic speaking feedback does not tell them which explanation problem to fix first.
- They need private practice before a high-stakes conversation.

Product promise:

> Practice one technical explanation, get one evidence-backed target, retry the same task and see whether that target moved.

## Competitive inspiration

Use competitors as inspiration, not as scope expansion.

| Product | Useful lesson | What AuraCoach should avoid copying |
| --- | --- | --- |
| Wispr Flow | Voice interfaces win when speaking feels faster than typing and cleanup is automatic. | Do not become a general dictation tool. AuraCoach is for rehearsal and feedback, not system-wide text input. |
| Yoodli | Speech coaching needs concrete practice moments and scalable feedback. | Do not claim broad coaching quality without human benchmarks and live reliability evidence. |
| Orai | Users understand feedback categories like clarity, filler words and pace. | Do not over-index on generic public speaking dimensions or confidence claims. |
| Poised | Workplace communication tools need privacy and trust language. | Do not analyze meetings, calendars, video presence or emotions in this prototype. |

Source scan:

- Wispr Flow official site and Google Play listing position it as AI voice-to-text that cleans up natural speech.
- Yoodli official site positions around AI speech coaching and organization-specific training.
- Orai Google Play listing positions around public speaking practice, filler words, pace, clarity, confidence and conciseness.
- Poised official site positions around meeting communication analytics and privacy.

## Product principles

- Start with the actual workflow, not a landing page.
- Keep the first scenario explicit: explain a technical project to a recruiter or nontechnical listener in 60 seconds.
- Keep video local for self-review.
- Upload only extracted mono PCM16 WAV audio when the user requests AI feedback.
- Show one target and one drill, not a decorative list of scores.
- Treat model output as untrusted until schema-validated.
- Let the evaluator abstain when evidence is weak.
- Compare retries only inside the same scenario, audience, goal and rubric context.
- Do not claim long-term personalization or learning outcomes until measured.

## Prompting and judging loop

Every AI improvement should follow this loop:

```text
task -> model output -> schema validation -> evidence check -> deterministic metrics -> user-facing feedback -> review -> fixture/regression update
```

Prompting standards:

- Prompt builder is versioned code.
- User speech and scenario text are placed inside a delimited untrusted context block.
- The evaluator is told not to score body language, emotion, confidence, eye contact or visual presence.
- The evaluator must support feedback with transcript evidence or abstain.
- Prompt/model/schema/rubric/metric versions are returned and persisted.

Judging standards:

- Completed feedback requires usable transcript evidence.
- Abstained feedback cannot render fake scores, drills or comparison claims.
- Filler count, WPM and duration are computed outside the model.
- Retry comparison is backend-owned and tied to the assigned target.
- Each new prompt or model change needs offline fixture validation and, when credentials are available, a live provider receipt.

## Engineering profile

The project should demonstrate:

- Software engineering: typed contracts, modular backend boundaries, migrations, idempotency, ownership isolation, CI and release runbooks.
- AI engineering: provider adapter, structured output, prompt-injection resistance, abstention, provenance and safe failure behavior.
- ML literacy: evaluation fixtures, baseline thinking, uncertainty, human-review readiness and no unsupported learning claims.
- Android product thinking: real-device testing, permissions, local media handling, release signing, Data safety and staged rollout.

## Lovable/Figma transfer brief

Use this when the Lovable connector is reauthenticated or when creating a Figma board:

```text
Create a product-design companion for AuraCoach, an Android-first AI communication practice app for technical builders.

The core user pain: technical people often understand their work but cannot explain it clearly to a recruiter, investor, customer or nontechnical teammate.

The product loop: setup -> record -> private review -> extracted-audio upload -> evidence-backed AI feedback -> one target -> retry -> comparison.

Design goals:
- Make the first screen the actual practice setup, not marketing.
- Make privacy visible: video stays local; extracted audio is uploaded only for feedback.
- Show the user's task context everywhere: scenario, audience, goal and target duration.
- Feedback must feel trustworthy: transcript evidence, provenance, abstention state and one target.
- Keep the tone calm, technical and credible for startup builders.

Screens:
1. Setup/context.
2. Recording with timer and permission clarity.
3. Review with local playback.
4. Feedback with evidence and one drill.
5. Retry comparison.
6. Release-readiness/audit checklist.

Do not add social sharing, broad dashboards, body-language scoring, emotion inference, gamification or generic speech categories.
```

## Review checklist

Before claiming a milestone is done:

- Did the code pass automated checks?
- Did the manual evidence match the claim?
- Did any media/privacy behavior change?
- Did docs distinguish shipped behavior from release blockers?
- Did prompt/schema/model changes update fixtures or receipts?
- Did the UX make the user problem clearer, or just add surface polish?

## Current highest-leverage gate

The next gate remains real-device Android proof:

```text
fresh short-path build -> install on authorized phone -> record -> extract WAV -> upload -> backend feedback/error -> receipt
```

Play Store visuals and broader prototype polish should wait until this gate passes.

