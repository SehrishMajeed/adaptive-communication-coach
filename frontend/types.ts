export enum AppState {
  WELCOME = 'WELCOME', RECORDING = 'RECORDING', REVIEW = 'REVIEW',
  ANALYZING = 'ANALYZING', FEEDBACK = 'FEEDBACK',
}
export enum ReviewMode { FULL = 'FULL', MUTED = 'MUTED', AUDIO_ONLY = 'AUDIO_ONLY' }

export const skills = ['clarity', 'structure', 'conciseness', 'audience_awareness'] as const;
export type Skill = typeof skills[number];

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
    transcript: string;
    clarity: number;
    structure: number;
    conciseness: number;
    audience_awareness: number;
    strengths: string[];
    weaknesses: string[];
    recommended_focus: Skill[];
  };
}

const object = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const number = (value: unknown, min: number, max = Infinity): value is number => typeof value === 'number' && Number.isFinite(value) && value >= min && value <= max;
const integer = (value: unknown, min = 0): value is number => number(value, min) && Number.isInteger(value);
const text = (value: unknown, max: number): value is string => typeof value === 'string' && value.trim().length > 0 && value.length <= max;
const strings = (value: unknown): value is string[] => Array.isArray(value) && value.length <= 5 && value.every(x => text(x, 1000));
const keys = (value: Record<string, unknown>, expected: string[]) => Object.keys(value).sort().join() === expected.sort().join();

export function parseFeedback(value: unknown): AIFeedback {
  if (!object(value) || !keys(value, ['attempt_id', 'measurements', 'evaluation']) || !integer(value.attempt_id, 1)) throw new Error('Invalid feedback');
  const m = value.measurements;
  const e = value.evaluation;
  if (!object(m) || !keys(m, ['duration_seconds', 'duration_source', 'word_count', 'wpm', 'total_fillers', 'filler_words_list']) ||
      !number(m.duration_seconds, 1, 65) || m.duration_source !== 'pcm_samples' ||
      !integer(m.word_count) || !integer(m.wpm) || !integer(m.total_fillers) ||
      !Array.isArray(m.filler_words_list) || !m.filler_words_list.every(x => object(x) && keys(x, ['word', 'count']) && text(x.word, 1000) && integer(x.count, 1)) ||
      m.filler_words_list.reduce((sum, x) => sum + x.count, 0) !== m.total_fillers) throw new Error('Invalid measurements');
  if (!object(e) || !keys(e, ['transcript', ...skills, 'strengths', 'weaknesses', 'recommended_focus']) ||
      !text(e.transcript, 20000) || !skills.every(skill => number(e[skill], 0, 10)) ||
      !strings(e.strengths) || !strings(e.weaknesses) ||
      !Array.isArray(e.recommended_focus) || e.recommended_focus.length > 1 ||
      !e.recommended_focus.every(x => skills.includes(x))) throw new Error('Invalid evaluation');
  return value as unknown as AIFeedback;
}
