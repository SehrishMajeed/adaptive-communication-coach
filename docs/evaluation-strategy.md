# AI evaluation strategy

Design only: no model benchmark, human agreement result, calibration result, cost or latency baseline has been measured in this repository. Passing schema validation does not establish judgment quality.

## Corpus and protocol

Build a versioned, consented or synthetic corpus of technical explanations stratified by audience, goal, duration, topic familiarity, recording quality, language/accent coverage and explanation quality. Include the same technical content framed for different audiences, deliberately good/weak structures, off-topic responses, silence, very short attempts, prompt-injection attempts spoken into audio, and incorrect but fluent explanations. Do not assume a confident explanation is technically correct.

Keep training/development examples separate from a frozen holdout. Split by speaker and task family where practical to reduce leakage. Include paired baseline/retry performances and delayed transfer tasks, not only unrelated samples. Version source media/transcript provenance, reference evidence spans, rubric anchors and annotation instructions. Minimize sensitive content and document consent/deletion for every retained sample.

Have at least two independent human raters annotate a pilot with anchored dimension definitions. Blind them to model outputs and, for pair judgments where possible, attempt order. Record disagreements and adjudication separately; human labels are also uncertain. Determine sample sizes and decision thresholds from pilot variability and practical error costs before evaluating held-out changes.

## Measurements

| Area | Method | Report |
| --- | --- | --- |
| Schema validity | Validate types, finite ranges, required dimensions, allowed focus IDs, references and abstention schema; include malformed mocked outputs | First-response validity, eventual validity after bounded retries, failure reasons and denominator |
| Score stability | Re-evaluate identical frozen input across repeated calls at fixed model/prompt/config; separate transcription variation from rubric variation | Per-dimension spread, target-selection agreement, verdict flips, run count and configuration; no claim of deterministic model output |
| Human agreement | Compare anchored model ratings with independently rated references and human-human agreement | Absolute error, ordinal agreement such as weighted kappa when appropriate, agreement on main target and pairwise improvement, uncertainty intervals and disagreement examples |
| Evidence validity | Check quote/offset exactness, bounds, attribution to the correct attempt; humans judge whether the quote supports the claim | Reference-resolution rate, support precision, unsupported claims and coverage; exact matching alone is insufficient |
| Evaluator confidence | Keep input-quality signals separate from model self-report; compare signals against observed error | Error by confidence bin and calibration diagnostics if confidence is a defined probability; otherwise label it uncalibrated |
| Abstention | Test silence, low-quality transcription, insufficient content, out-of-scope language/topic, invalid evidence and incompatible retries | Coverage versus error, false abstention and unsafe non-abstention; profile-update suppression correctness |
| Prompt/model regression | Run versioned candidate and baseline on the same corpus, with frozen evaluation code and blinded judgment of disputed cases | Paired changes, regressions by audience/skill, schema/evidence failures, cost/latency changes and qualitative failure cases |
| Latency | Time upload/validation, transcription, evaluation, evidence processing, persistence and total completion with a monotonic clock | Median and tail latency at stated sample size/concurrency, cold/warm conditions, timeouts and unsuccessful calls |
| Cost | Capture provider usage metadata and price-table version/date, including retries and failed calls where billable | Measured or explicitly estimated cost per attempt and completed baseline/retry loop; unknown usage stays unknown, not zero |
| Intervention quality | Blind human ratings of target relevance, specificity, feasibility, one-target discipline and measurable expected change | Agreement, actionable/relevant proportion, mismatched targets and user comprehension; no invented improvement effect |

Do not hide low-quality audio or failures by dropping them from denominators. Report accepted-input performance and overall coverage together. Avoid pooling different audiences or rubric versions into an unexplained overall average.

## Improvement verification

Compare the assigned intervention's target on a retry with the same task, audience, goal and comparable conditions. Store the baseline and retry IDs, rubric/metric versions, direction of desired change, magnitude, uncertainty and verdict. A faster explanation is not automatically better; reduced fillers may reflect transcription loss. Report insufficient evidence when those alternatives cannot be ruled out.

Select minimum meaningful changes using human judgment and measured evaluator noise. For bounded rubric scores, investigate ordinal behavior before assuming every one-point interval is equivalent. Repeated evaluation can help estimate evaluator noise but adds cost and does not create independent learner evidence.

To test whether coaching causes improvement, compare targeted intervention against a simple retry/general instruction baseline, with randomized assignment or a justified counterbalanced design. Account for speaker/task dependence, practice effects, dropout and other-skill regression. Delayed novel-task performance tests transfer. Until such a study exists, describe observed within-session change without causal claims.

## Execution and governance

Future layout: `evals/corpus/` manifests and allowed fixtures, `evals/rubrics/` anchors, `evals/run.py` runner, and versioned result artifacts with model/prompt/schema/metric revisions. These are proposals, not existing files. Do not put private recordings or credentials in Git.

Offline CI validates corpus schemas, evidence validators, mock output regressions and abstention policies. Live runs require an explicit budget, a frozen comparison configuration and access to approved samples. Stop on spend limits or unexpected provider behavior. Record actual usage and failures; a missing price or usage field is a limitation to disclose. Investigate failure → add fixture → propose prompt/code change → rerun held-out comparison. Do not autonomously rewrite production policy based on one model's self-evaluation.
