# ADR 0003: structured evidence instead of generic conversational memory

Status: accepted direction; present profile fields are incomplete precursors.

## Context

Personalization needs to explain which task, audience, observation and intervention support an estimate. Free-form conversation history and latest-strength lists cannot establish comparable attempts or prevent duplicate updates.

## Decision

Persist owned sessions, attempts, versioned measurements/evaluations, eligible skill evidence, interventions and rebuildable profiles. Supply only relevant structured context to future evaluation/coaching. Record abstention and provenance explicitly. Do not introduce embeddings or a vector database.

## Alternatives

Append all chats to each prompt: easy initially but costly, hard to validate and privacy-heavy. Store averages only: compact but loses lineage, uncertainty and correction/deletion ability. Raw model prose cannot be the authoritative learner state.

## Consequences

Schema design, migrations, idempotency, ownership and retention matter early. More structured records are required, but no new service is necessary. Profiles can be recomputed after evidence correction, policy change or deletion, and incompatible audiences need not collapse into one misleading score.
