import { parsePracticeAttemptHistory, parsePracticeAttemptResult, PracticeAttemptHistory, PracticeAttemptResult, PracticeSetup } from '../types';
import { prepareAudio } from './audio';
import type { Recording } from './recording';

const apiBase = () => import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const randomId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) return crypto.randomUUID();
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export const getOwnerToken = () => {
  const key = 'aura_owner_token';
  try {
    const existing = localStorage.getItem(key);
    if (existing) return existing;
    const created = randomId();
    localStorage.setItem(key, created);
    return created;
  } catch {
    return randomId();
  }
};

const defaultSetup: PracticeSetup = {
  scenario: 'Explain a technical project to a non-technical person in 60 seconds.',
  audience: 'recruiter or non-technical interviewer',
  goal: 'make the project understandable and relevant',
  requested_duration_seconds: 60,
};

export const createPracticeSession = async (setup: PracticeSetup = defaultSetup): Promise<number> => {
  const response = await fetch(`${apiBase()}/api/practice-sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Owner-Token': getOwnerToken() },
    body: JSON.stringify(setup),
  });
  if (!response.ok) throw new Error('The backend could not create a practice session. Please try again.');
  const body = await response.json();
  if (!body || typeof body.session_id !== 'number') throw new Error('The backend returned an invalid session. Please try again.');
  return body.session_id;
};

export const analyzeRecording = async (recording: Recording, sessionId?: number | null, setup: PracticeSetup = defaultSetup): Promise<PracticeAttemptResult> => {
  let audio: Blob;
  try { audio = await prepareAudio(recording.audioBlob); }
  catch { throw new Error('Audio could not be prepared. You can review this recording or record again in another browser.'); }

  const activeSessionId = sessionId ?? await createPracticeSession(setup);
  const form = new FormData();
  form.append('audio', audio, 'recording.wav');
  form.append('duration_seconds', String(recording.durationSeconds));
  form.append('idempotency_key', randomId());
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);
  try {
    const response = await fetch(`${apiBase()}/api/practice-sessions/${activeSessionId}/attempts`, {
      method: 'POST',
      headers: { 'X-Owner-Token': getOwnerToken() },
      body: form,
      signal: controller.signal,
    });
    if (!response.ok) {
      if (response.status === 422 || response.status === 413) throw new Error('The recording was rejected. Record 1-60 seconds and try again.');
      if (response.status === 502) throw new Error('The evaluator could not process this recording. Please try again.');
      throw new Error('The backend could not save or process the recording. Please try again.');
    }
    try { return parsePracticeAttemptResult(await response.json()); }
    catch { throw new Error('The backend returned an invalid result. Please try again.'); }
  } catch (error) {
    if (controller.signal.aborted || error instanceof TypeError) {
      throw new Error('The request could not finish. Check your connection and try again.');
    }
    throw error;
  } finally { clearTimeout(timeout); }
};

export const fetchPracticeSessionHistory = async (sessionId: number): Promise<PracticeAttemptHistory> => {
  const response = await fetch(`${apiBase()}/api/practice-sessions/${sessionId}/attempts`, {
    method: 'GET',
    headers: { 'X-Owner-Token': getOwnerToken() },
  });
  if (!response.ok) throw new Error('The backend could not load this session history.');
  try { return parsePracticeAttemptHistory(await response.json()); }
  catch { throw new Error('The backend returned invalid session history.'); }
};
