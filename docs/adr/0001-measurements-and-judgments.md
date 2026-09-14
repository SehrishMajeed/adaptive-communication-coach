# ADR 0001: deterministic measurements versus probabilistic judgments

Status: accepted direction; current implementation has violations.

## Context

Duration, counts and deltas are calculable, while clarity and audience fit require interpretation. The prototype's byte-duration estimate and unchecked scores make both appear more certain than their inputs support.

## Decision

Code owns measurable calculations and their provenance. AI owns bounded, versioned qualitative judgments with validated evidence. Persist the distinction, including input reliability and unavailable/abstained states. Transcript-derived counts remain conditional on transcription fidelity. Do not convert evaluator confidence into a speaking-skill score.

## Alternatives

Ask one model for all numbers: simpler integration, but unverifiable arithmetic and measurement drift. Use only mechanical metrics: reproducible, but misses the core explanatory-quality problem. Neither provides the needed boundary.

## Consequences

We need reliable duration/media handling, transcript quality signals, typed contracts and separate tests for calculation versus interpretation. Evaluation requires human agreement and evidence audits in addition to schema checks. The boundary supports recomputation and diagnosis without replacing the model provider.
