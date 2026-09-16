export const skills = ['clarity', 'structure', 'conciseness', 'audience_awareness'] as const;
export type Skill = typeof skills[number];

export interface PracticeSetup {
  scenario: string;
  audience: string;
  goal: string;
  requested_duration_seconds: number;
}

export interface AIFeedback {
  attempt_id: number;
  measurements: {
    duration_seconds: number;
    duration_source: 'pcm_samples';
    word_count: number;
    wpm: number;
    total_fillers: number;
    filler_words_list: { word: string; count: number }[];
  };
  evaluation: {
    evaluator_status: 'completed' | 'abstained';
    abstention_reason: string | null;
    input_quality: 'usable' | 'limited' | 'unusable';
    evidence_status: 'quote_verified' | 'insufficient_evidence' | 'unavailable';
    feedback_status: 'actionable' | 'needs_retry' | 'abstained';
    transcript: string;
    clarity: number | null;
    structure: number | null;
    conciseness: number | null;
    audience_awareness: number | null;
    strengths: string[];
    weaknesses: string[];
    recommended_focus: Skill[];
    evidence: { skill: Skill; quote: string; note: string }[];
  };
  provenance: {
    prompt_version: string;
    model_id: string;
    schema_version: string;
    rubric_version: string;
    metric_version: string;
  };
}

export interface BackendComparison {
  comparison_id: number;
  baseline_attempt_id: number;
  retry_attempt_id: number;
  intervention_id: number;
  target_skill: Skill;
  comparability_status: 'comparable' | 'insufficient_evidence' | 'context_mismatch' | 'rubric_mismatch';
  verdict: 'improved' | 'no_clear_change' | 'regressed' | 'insufficient_evidence';
  deltas: Record<string, number>;
}

export interface BackendWorkflow {
  route: 'abstained' | 'baseline' | 'baseline_blocked' | 'retry_comparable' | 'retry_blocked' | 'retry_without_baseline';
  reason: 'abstained_evaluation' | 'first_eligible_attempt' | 'first_attempt_not_eligible' | 'retry_eligible_with_baseline' | 'retry_not_eligible' | 'missing_prior_intervention' | 'baseline_not_eligible';
  creates_intervention: boolean;
  creates_comparison: boolean;
}

export interface PracticeAttemptResult {
  sessionId: number;
  sequenceNumber: number;
  feedback: AIFeedback;
  workflow: BackendWorkflow;
  comparison: BackendComparison | null;
}

export interface PracticeAttemptHistory {
  sessionId: number;
  attempts: PracticeAttemptResult[];
}

const object = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const number = (value: unknown, min: number, max = Infinity): value is number => typeof value === 'number' && Number.isFinite(value) && value >= min && value <= max;
const integer = (value: unknown, min = 0): value is number => number(value, min) && Number.isInteger(value);
const text = (value: unknown, max: number): value is string => typeof value === 'string' && value.trim().length > 0 && value.length <= max;
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.length <= 5 && value.every(x => text(x, 1000));
const keys = (value: Record<string, unknown>, expected: string[]) => Object.keys(value).sort().join() === expected.sort().join();

export function parseFeedback(value: unknown): AIFeedback {
  if (!object(value) || !keys(value, ['attempt_id', 'measurements', 'evaluation', 'provenance']) || !integer(value.attempt_id, 1)) throw new Error('Invalid feedback');
  const m = value.measurements;
  const e = value.evaluation;
  const p = value.provenance;
  if (!object(m) || !keys(m, ['duration_seconds', 'duration_source', 'word_count', 'wpm', 'total_fillers', 'filler_words_list']) ||
      !number(m.duration_seconds, 1, 65) || m.duration_source !== 'pcm_samples' ||
      !integer(m.word_count) || !integer(m.wpm) || !integer(m.total_fillers) ||
      !Array.isArray(m.filler_words_list) || !m.filler_words_list.every(x => object(x) && keys(x, ['word', 'count']) && text(x.word, 1000) && integer(x.count, 1)) ||
      m.filler_words_list.reduce((sum, x) => sum + x.count, 0) !== m.total_fillers) throw new Error('Invalid measurements');
  if (!object(e) || !keys(e, ['evaluator_status', 'abstention_reason', 'input_quality', 'evidence_status', 'feedback_status', 'transcript', ...skills, 'strengths', 'weaknesses', 'recommended_focus', 'evidence']) ||
      (e.evaluator_status !== 'completed' && e.evaluator_status !== 'abstained') ||
      !['usable', 'limited', 'unusable'].includes(String(e.input_quality)) ||
      !['quote_verified', 'insufficient_evidence', 'unavailable'].includes(String(e.evidence_status)) ||
      !['actionable', 'needs_retry', 'abstained'].includes(String(e.feedback_status)) ||
      typeof e.transcript !== 'string' || e.transcript.length > 20000 ||
      !strings(e.strengths) || !strings(e.weaknesses) ||
      !Array.isArray(e.recommended_focus) || e.recommended_focus.length > 1 ||
      !e.recommended_focus.every(x => skills.includes(x)) ||
      !Array.isArray(e.evidence) || e.evidence.length > 8 ||
      !e.evidence.every(x => object(x) && keys(x, ['skill', 'quote', 'note']) && skills.includes(x.skill as Skill) && text(x.quote, 500) && text(x.note, 1000))) throw new Error('Invalid evaluation');
  const scoreValues = skills.map(skill => e[skill]);
  if (e.evaluator_status === 'completed') {
    if (!text(e.transcript, 20000) || scoreValues.some(score => !number(score, 0, 10)) ||
        e.abstention_reason !== null || e.input_quality === 'unusable' ||
        e.evidence_status !== 'quote_verified' || e.feedback_status !== 'actionable' ||
        e.evidence.length === 0 ||
        !e.evidence.every(x => String(e.transcript).toLowerCase().includes(String(x.quote).toLowerCase()))) throw new Error('Invalid evaluation');
  } else if (scoreValues.some(score => score !== null) || e.abstention_reason === null ||
      e.input_quality === 'usable' || e.evidence_status === 'quote_verified' ||
      e.feedback_status !== 'abstained' || e.recommended_focus.length !== 0 || e.evidence.length !== 0) {
    throw new Error('Invalid evaluation');
  }
  if (!object(p) || !keys(p, ['prompt_version', 'model_id', 'schema_version', 'rubric_version', 'metric_version']) ||
      !text(p.prompt_version, 200) || !text(p.model_id, 200) || !text(p.schema_version, 200) ||
      !text(p.rubric_version, 200) || !text(p.metric_version, 200)) throw new Error('Invalid provenance');
  return value as unknown as AIFeedback;
}

function parseComparison(value: unknown): BackendComparison | null {
  if (value === null) return null;
  if (!object(value) || !keys(value, [
    'comparison_id', 'baseline_attempt_id', 'retry_attempt_id', 'intervention_id',
    'target_skill', 'comparability_status', 'verdict', 'deltas',
  ])) throw new Error('Invalid comparison');
  if (!integer(value.comparison_id, 1) || !integer(value.baseline_attempt_id, 1) ||
      !integer(value.retry_attempt_id, 1) || !integer(value.intervention_id, 1) ||
      !skills.includes(value.target_skill as Skill) ||
      !['comparable', 'insufficient_evidence', 'context_mismatch', 'rubric_mismatch'].includes(String(value.comparability_status)) ||
      !['improved', 'no_clear_change', 'regressed', 'insufficient_evidence'].includes(String(value.verdict)) ||
      !object(value.deltas) || !Object.values(value.deltas).every(delta => typeof delta === 'number' && Number.isFinite(delta))) {
    throw new Error('Invalid comparison');
  }
  return value as unknown as BackendComparison;
}

function parseWorkflow(value: unknown): BackendWorkflow {
  if (!object(value) || !keys(value, ['route', 'reason', 'creates_intervention', 'creates_comparison'])) throw new Error('Invalid workflow');
  if (!['abstained', 'baseline', 'baseline_blocked', 'retry_comparable', 'retry_blocked', 'retry_without_baseline'].includes(String(value.route)) ||
      !['abstained_evaluation', 'first_eligible_attempt', 'first_attempt_not_eligible', 'retry_eligible_with_baseline', 'retry_not_eligible', 'missing_prior_intervention', 'baseline_not_eligible'].includes(String(value.reason)) ||
      typeof value.creates_intervention !== 'boolean' || typeof value.creates_comparison !== 'boolean') {
    throw new Error('Invalid workflow');
  }
  return value as unknown as BackendWorkflow;
}

export function parsePracticeAttemptResult(value: unknown): PracticeAttemptResult {
  if (!object(value) || !keys(value, ['attempt_id', 'session_id', 'sequence_number', 'measurements', 'evaluation', 'provenance', 'workflow', 'intervention', 'comparison']) ||
      !integer(value.session_id, 1) || !integer(value.sequence_number, 1)) throw new Error('Invalid attempt result');
  return {
    sessionId: value.session_id,
    sequenceNumber: value.sequence_number,
    feedback: parseFeedback({
      attempt_id: value.attempt_id,
      measurements: value.measurements,
      evaluation: value.evaluation,
      provenance: value.provenance,
    }),
    workflow: parseWorkflow(value.workflow),
    comparison: parseComparison(value.comparison),
  };
}

export function parsePracticeAttemptHistory(value: unknown): PracticeAttemptHistory {
  if (!object(value) || !keys(value, ['session_id', 'attempts']) ||
      !integer(value.session_id, 1) || !Array.isArray(value.attempts)) throw new Error('Invalid attempt history');
  const attempts = value.attempts.map(parsePracticeAttemptResult);
  if (!attempts.every(attempt => attempt.sessionId === value.session_id)) throw new Error('Invalid attempt history');
  return {
    sessionId: value.session_id,
    attempts,
  };
}
