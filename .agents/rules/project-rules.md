# Adaptive Communication Coach - Project Operating System

## 1. PRODUCT FIRST
Solve ONE coherent communication-coaching problem.
- DETERMINISTIC CODE = measurable truth (WPM, filler counts, duration).
- AI = qualitative interpretation and coaching (Clarity, Structure, Feedback).
- LANGGRAPH = state + workflow orchestration.
- DATABASE = structured durable evidence (Progress over time).
- REACT = interaction and presentation.
Never allow AI output to silently become authoritative numerical truth.

## 2. INTENTIONAL EXECUTION
- For architecture, schemas, security, LangGraph, persistence, APIs, migration, deployment: **INSPECT → PLAN → VERIFY → EXECUTE**.
- For small styling, renames, isolated tests: use fast execution.

## 3. CONTEXT ENGINEERING
Maintain concise project reference documents (e.g., `docs/architecture.md`). Do not dump giant prompts. Keep docs synced with code.

## 4. DOE ARCHITECTURE
- **Directive**: User goal, scenario, audience.
- **Orchestration**: LangGraph (validate → measure → evaluate → diagnose → coach → compare → update).
- **Execution**: Python deterministic code (calculations, API calls, DB writes). Orchestration must not reinvent execution logic.

## 5. CONTROL PROBABILISTIC VARIABILITY
- LLM output → Pydantic structured schema → validation → business logic → state update.
- NEVER parse free-form LLM paragraphs to control the application.

## 6. LLM + PYTHON DIVISION
- **Python**: Duration, WPM, filler count, score deltas, DB updates, routing logic.
- **AI**: Clarity, structure, audience awareness, coaching explanation, wording.
If deterministic code can reliably do it, DO NOT use an LLM.

## 7. MEMORY DESIGN
Persist structured evidence, not raw chat history. Retrieve only relevant context (metrics, rubric results, recurring strengths/weaknesses).

## 8. REFLECTION / SELF-IMPROVEMENT
No autonomous production code rewriting. Maintain an eval loop: failure case → fixture → evaluation → proposed fix → human review.

## 9. PARALLELIZATION
Parallelize only independent execution work (e.g., deterministic metric calculation + qualitative rubric evaluation) if dependencies permit. Do not create subagents purely for keywords.

## 10. SECURITY 80/20
- No secrets in frontend (never `VITE_*` API keys).
- Server-side request validation via Pydantic.
- Treat recordings/transcripts as untrusted input. Do not log full transcripts by default.

## 11. TESTING PYRAMID
Deterministic unit tests → LangGraph behavior tests → API integration with mocked providers → Frontend verification → Manual smoke test. CI must never require paid AI calls.

## 12. ARCHITECTURAL IDENTITY
"Deterministic Python establishes measurable truth, LangGraph orchestrates the adaptive learning loop, structured AI interprets communication quality, and persistent evidence allows future sessions to adapt."
