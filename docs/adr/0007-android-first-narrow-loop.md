# ADR 0007: Android-first narrow practice loop

Date: 2026-09-16

## Status

Accepted direction.

## Context

The project needs to demonstrate strong product judgment and engineering maturity without becoming a broad AI demo. The long-term product goal is an Android app available through Google Play, but the current implementation is a React web vertical slice that proves the capture, review, audio-only upload, Gemini evaluation and retry-comparison path.

The risk is spreading effort across too many speaking-coach features before the core painful problem is proven.

## Decision

The flagship product direction is Android-first, but the product scope remains one narrow loop:

> practice a one-minute technical project explanation for a recruiter or nontechnical listener, receive one improvement target, retry the same explanation and compare.

The current web app remains the technical proof. The backend must evolve next toward durable owned practice sessions before building the Android client.

The preferred first Android stack is React Native with TypeScript because it reuses the existing React/TypeScript skill and keeps Android delivery focused on media lifecycle, trust, permissions and UX. Native Kotlin modules may be added only for measured media, performance or platform limitations.

## Consequences

- Do not build a generic speaking coach, chatbot or body-language analyzer first.
- Do not start broad Android UI work before Phase 2 durable session architecture exists.
- Keep video local and make that privacy boundary visible in the product.
- Treat Google Play policy, Data safety disclosure, accessibility, crash reporting and device testing as release requirements.
- Show ML knowledge through evaluation discipline, uncertainty and baselines rather than premature model training.
- Keep resume claims tied to shipped code, tests, docs and verification receipts.

## Revisit when

- React Native media capture cannot satisfy reliability or privacy requirements on target Android devices.
- Durable backend session APIs are complete and ready for Android consumption.
- User testing shows a different first scenario has stronger pull than technical project explanation.
