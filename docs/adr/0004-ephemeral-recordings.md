# ADR 0004: raw recordings are ephemeral by default

Status: accepted direction; present audiovisual upload and tracing defaults need correction.

## Context

Video helps self-review, while the initial backend needs audio for transcription/evaluation. Recordings and transcripts may disclose personal or confidential technical information. Avoiding a blob database column alone does not establish privacy across uploads, traces and providers.

## Decision

Keep video local. Process necessary audio ephemerally with bounded lifetimes and cleanup on all paths. Exclude raw payloads from logs/traces/checkpoints by default. Retain only consented, owned structured evidence and necessary transcript content under a defined deletion policy. Verify external provider retention settings separately; do not promise deletion outside our control.

## Alternatives

Store all recordings for replay/research: increases exposure and operational burden beyond the initial need. Process everything locally: potentially valuable, but requires capability/quality work not justified now. Explicit research retention may be added later with separate consent and controls.

## Consequences

Users may lose replay after leaving the local session. Temporary upload spooling still needs cleanup. Evidence excerpts and transcripts remain sensitive and require deletion/export rules. Debugging uses metadata and approved fixtures rather than unrestricted production recordings.
