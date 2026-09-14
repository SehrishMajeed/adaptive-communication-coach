# Product direction

Status: intended product, not a description of shipped capabilities. See [current audit](current-state-audit.md).

## User and problem

CS students, software engineers, AI/ML engineers, researchers, and technical founders need to explain complex ideas to people with different knowledge and priorities. Understanding a system does not ensure that its explanation is understandable, relevant, or well structured. Generic feedback does not identify a useful practice target or establish whether practice helped.

## Value proposition and initial wedge

Help a technical person explain one technical concept or project to a specified audience, practice one observable weakness, and compare a retry against the same task. Begin with a short explanation and a small, explicit rubric. Recruiters, engineers, product managers, investors, and nontechnical listeners need different explanations; audience and communication goal are part of the task, not optional prompt decorations.

Primary use case: explain a project to a recruiter in one minute, identify the most consequential supported weakness, do a targeted exercise, and retry that explanation. Generalize task duration to 30 seconds, 1, 3, 5, and 10 minutes only after capture and measurement are reliable.

## Product loop

Choose topic, audience, goal, and duration → record → deliberately review → measure and evaluate → validate evidence → diagnose → select one target and exercise → retry the same task → compare the target → report improvement, no clear change, regression, or insufficient evidence → update structured skill history only when justified.

Full Review plays video and audio; Presence Review plays muted video; Voice Review plays audio only. These are user reflection tools, not automated body-language or emotional assessment. The initial backend receives audio only; local video is for self-review.

## Principles

- Code calculates reproducible measurements from explicitly qualified inputs. A deterministic calculation over an uncertain transcript is not certainty about the original speech.
- AI gives bounded qualitative judgments supported by identifiable evidence. Its confidence is not the user's confidence.
- Present one actionable priority with supporting evidence, rather than a collection of decorative scores.
- Preserve task context across retries. A changed audience or goal starts a different comparison context.
- A score increase is an observation, not proof that coaching caused improvement. Admit uncertainty and abstain when needed.
- Use structured, deletable evidence for personalization; minimize collection and retention.
- Keep the existing stack and modular monolith until measured needs justify change.

## Non-goals

Generic public speaking coaching, chat companionship, social/community features, visual scoring, emotion inference, RAG, vector databases, MCP, multi-agent systems, microservices, PyTorch, fine-tuning, reinforcement learning, and complex cognitive diagnosis are outside the initial scope. No major UI redesign during the correctness stage.

## Candidate success metrics

Define instruments and baselines before targets; no results exist yet.

| Question | Candidate measure | Guardrail |
| --- | --- | --- |
| Can users finish practice? | Valid baseline-to-retry completions / started sessions | Separate abandonment, input failure, and provider failure |
| Is feedback defensible? | Evidence-supported judgments / audited judgments | Also report abstention and unsupported-claim rates |
| Did the target improve? | Paired, human-rated target change on comparable attempts | Report uncertainty, missing retries, and regression in other skills |
| Is the intervention useful? | User comprehension and human-rated actionability | Do not substitute satisfaction for learning |
| Does learning persist? | Delayed performance on a new comparable task | Separate memorized retries from transfer |
| Is the system practical? | Completion latency, error rate, cost per completed loop | Include failed calls, retries, and dropped sessions |
