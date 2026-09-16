# Product thesis: painkiller wedge

Status: product strategy and validation plan, not shipped capability. The goal is to turn an unspoken pain into a narrow product loop that can be verified before scaling.

## Builder positioning

This project should present the builder as a CS student focused on AI engineering, agentic systems, and practical AI products with Python, React, and modern AI tools.

The honest current positioning is:

> Practical AI product now; clear path toward agentic coaching after the retry/intervention loop becomes durable, evidence-grounded, and profile-safe.

That means the repository should show:

- product taste: one painful user problem, not a generic AI wrapper;
- AI engineering: provider isolation, schema validation, prompt discipline, failure boundaries, and cost/privacy awareness;
- agentic thinking: a prototype retry loop today and a future stateful coaching loop with explicit validation, diagnosis, intervention, durable comparison, and evidence-gated profile updates, without claiming that full loop is shipped today;
- software engineering: tests, documentation, architecture decisions, honest limitations, and reproducible setup;
- restraint: no claims of personalization, production readiness, or verified improvement until the system earns them.

## Core goal

Build the fastest private rehearsal loop for technical people who know their work but cannot reliably explain it when the stakes are real.

The product should make users feel:

> "I knew I was not explaining myself well, but I could not name the problem. This shows me the one thing to fix and lets me prove I improved."

This is not a generic public speaking app. It is a high-stakes explanation coach for interviews, demos, portfolio walkthroughs, investor/user conversations, stakeholder updates, and technical presentations.

## Focused painful problem

Technical people often have three simultaneous problems:

1. They understand the subject internally but cannot translate it for a listener with different context.
2. They receive vague advice such as "be clearer" or "sound more confident" without evidence or a next drill.
3. They avoid repetitions because practice feels embarrassing, unstructured, and hard to measure.

The unspoken pain is not "I need public speaking lessons." The sharper pain is:

> "When it matters, my explanation does not land, and I do not know exactly why."

For the first focused product, solve this one job:

> Help a technical person turn a confusing one-minute explanation into a listener-ready explanation through one diagnosis, one drill, and one retry.

## Why this is worth testing

Evidence from public sources supports the direction, but not yet this exact product:

- Employers consistently value communication. NACE reported that written communication was important to at least 70% of responding employers in its Job Outlook 2025 resume-screening data.
- LinkedIn listed communication as the top in-demand skill in 2024.
- Public speaking anxiety and fear of evaluation are persistent issues among students and professionals; recent research continues to frame speaking anxiety as a significant educational and career barrier.
- Existing products prove demand for adjacent loops: Orai offers phone/web speech coaching with feedback on fillers, pace, clarity, energy and conciseness; Yoodli positions itself around realistic roleplays, instant insights, progress, and enterprise training; ELSA has scaled around AI speech practice, pronunciation, roleplay, and real-world scenarios.
- Large habit products such as Duolingo show the power of bite-sized practice, streaks, progress loops, and emotionally simple daily actions, but those mechanics should support the learning loop rather than replace evidence.

These signals justify exploration. They do not prove product-market fit. The product must earn that through user validation and measured completion/retry behavior.

## Product pattern to copy

Copy the pattern, not the feature list.

| Pattern | Seen in successful products | How Aura Coach should use it |
| --- | --- | --- |
| One painful job | Grammarly improves writing before sending; ELSA improves spoken English; Orai improves speech practice | Start with one-minute technical explanations, not every speaking use case |
| Private safe rehearsal | Speech apps let users practice before the real moment | Keep video local, upload audio only, make privacy obvious |
| Immediate feedback | Grammarly/Orai/ELSA reduce the delay between action and correction | Return one evidence-backed diagnosis quickly |
| One next action | Duolingo/Headspace reduce cognitive load with a small daily action | Give one drill, not a dashboard of scores |
| Retry loop | Learning apps make improvement visible through repeated attempts | Compare the same task, same audience, same goal |
| Progress memory | Habit products remember streak/progress; coaching tools track growth | Store versioned evidence and show honest trend only after enough data |
| Trust boundary | Mental health/learning products win through safety and credibility | Admit uncertainty, abstain when evidence is weak, never invent visual feedback |

## Product promise

Recommended promise:

> Practice your technical explanation. Get the one change that will make it land. Retry and see if it improved.

Avoid these promises until verified:

- "Become confident."
- "Guaranteed interview success."
- "AI knows your body language."
- "Scientifically proven improvement."
- "Personalized learning path" before evidence and profile logic exist.

## Initial user wedge

Primary user:

- CS students, junior software engineers, AI/ML engineers, technical founders, and portfolio builders preparing for interviews, demos, or project explanations.

Initial scenario:

- "Explain a technical project to a recruiter or nontechnical interviewer in 60 seconds."

Why this wedge:

- It is frequent, high-stakes, painful, and narrow enough to evaluate.
- The user already has content but struggles with translation, structure, conciseness, audience fit, and delivery.
- It aligns with the existing backend: audio capture, transcript, deterministic metrics, bounded rubric, retry comparison.

## Product loop

1. Choose one scenario: recruiter, hiring manager, nontechnical stakeholder, investor, teammate, or customer.
2. State the project/topic in one sentence.
3. Record 60 seconds.
4. Review locally: full replay, muted presence, audio-only voice.
5. Get AI feedback with transparent evidence.
6. Receive exactly one priority: clarity, structure, conciseness, or audience awareness.
7. Do a short drill targeted to that priority.
8. Retry the same explanation.
9. See one comparison: improved, no clear change, regressed, or insufficient evidence.
10. Save evidence only when ownership, consent, and validity are established.

## What the app should feel like

- Calm, private, and premium rather than flashy.
- More like a trusted coach than a score machine.
- Focused on "say it better for this listener" rather than "perform perfectly."
- Honest about uncertainty: if the transcript is weak, the app should say so.
- Built for quick mobile use: open, practice, learn one thing, retry.

## System direction

Proceed in this order:

1. Finish PR 1 manual acceptance: live Gemini path, real browser recording, audio-only upload, replay modes, and recoverable errors.
2. Implement Phase 2A domain schema and Alembic migrations before shared-user history.
3. Add anonymous ownership and session context before any personalization.
4. Promote the in-memory baseline-to-retry loop into a durable, owned session model for one fixed scenario.
5. Add evidence-grounded evaluation before claiming adaptive coaching.
6. Build the Android client after the backend loop has durable sessions, ownership and comparable retry semantics.

The current React web app remains a proof of the capture/evaluation path. The Android product should reuse the same backend contracts and follow [Android-first system design](android-first-system-design.md).

## Validation questions

Treat these as hypotheses:

1. Do technical users recognize the pain within 10 seconds of seeing the concept?
2. Can they complete baseline feedback and retry in under five minutes?
3. Do they trust the feedback because it quotes or references their own explanation?
4. Does "one priority" feel more useful than many scores?
5. Does the retry comparison make them want another practice session?
6. Are users willing to submit non-confidential project explanations when audio-only privacy is clear?
7. Which scenario has strongest pull: recruiter intro, technical interview answer, product demo, investor pitch, or stakeholder update?

## Success metrics to instrument later

- Baseline recording completion rate.
- Feedback request success rate.
- Retry rate after first feedback.
- Time from opening app to first useful diagnosis.
- Percentage of feedback with valid transcript and evidence.
- User-rated "this named my real problem" score.
- Same-session target improvement rate, reported with uncertainty.
- Seven-day return rate after a meaningful first retry.

Do not optimize streaks or notifications until the first-retry loop proves valuable.

## Product red lines

- Do not send video to the backend or provider.
- Do not infer body language automatically in the initial product.
- Do not store raw audio as durable evidence.
- Do not treat model confidence as user confidence.
- Do not let shared demo or anonymous prototype data become real learner history.
- Do not build broad dashboards before one loop works.

## Source notes

- NACE, "What Are Employers Looking for When Reviewing College Students' Resumes," 2024.
- LinkedIn, "The Most In-Demand Skills of 2024."
- Orai App Store / Google Play and Orai product site, speech coaching positioning and download/social proof.
- Yoodli product and help pages, AI roleplay and communication practice positioning.
- ELSA Speak Google Play and product pages, AI speech learning, pronunciation, roleplay, and scale signals.
- Duolingo investor updates and product blog, bite-sized practice and habit loop evidence.
- Headspace product pages and app-based mindfulness research are useful as trust/safety pattern references, not as direct feature models.
