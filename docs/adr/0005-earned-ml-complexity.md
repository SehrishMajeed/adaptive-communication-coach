# ADR 0005: introduce ML complexity only after baseline evaluation

Status: accepted direction; no advanced learner model is required initially.

## Context

Sparse, noisy, correlated attempts do not justify complex personalization models. A sophisticated estimator over unreliable evaluations can be confidently wrong, and portfolio value does not substitute for experimental evidence.

## Decision

Begin with interpretable summaries and explicit eligibility. Compare simple averages and EMA on properly split longitudinal data before uncertainty-aware or Bayesian/state-space models. Adopt additional complexity only for reproducible improvement on a defined practical objective with acceptable maintenance/cost. No PyTorch, fine-tuning, RL or neural diagnosis in the first stage.

## Alternatives

Implement a neural model immediately: higher data and explanation burden without a baseline. Use a permanent unqualified average: simple but ignores uncertainty and context. A measured escalation path preserves simplicity without ruling out useful research.

## Consequences

Early engineering goes into evidence quality, held-out data, provenance and evaluation. Research may conclude that a simple method is best or that data are insufficient. Both are valid outcomes. Experimental sophistication is measured by rigor, not model size.
