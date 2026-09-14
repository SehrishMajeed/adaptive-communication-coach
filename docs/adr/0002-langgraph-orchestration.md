# ADR 0002: use LangGraph for conditional coaching orchestration

Status: accepted direction; current graph implements only evaluation, metrics and a retry branch.

## Context

The intended loop must distinguish unusable input, a baseline, a comparable retry, insufficient evidence and target outcomes. These transitions need explicit tests. LangGraph is already in the stack, so replacement needs a stronger reason than preference.

## Decision

Retain a small typed graph to route those outcomes and call bounded domain/provider services. Keep arithmetic, authorization and transactions outside graph policy. Use one backend process initially; no multi-agent system. Persistence owns durable evidence, not graph history.

## Alternatives

A normal application service with conditionals is viable for a simpler workflow and remains the fallback if the graph adds no clarity. Multiple agents introduce uncontrolled variability and cost without an identified need. A graph wrapping only one unconditional model call is not sufficient justification.

## Consequences

Test the compiled graph and its failure branches with fake providers. Do not parallelize metrics before transcription exists. Raw media must not enter durable checkpoints or unrestricted traces. Add resumable jobs/checkpoints only after a measured recovery or latency need.
