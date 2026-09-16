import { Platform } from 'react-native';
import { parsePracticeAttemptHistory, parsePracticeAttemptResult, PracticeAttemptHistory, PracticeAttemptResult, PracticeSetup } from '../../../shared/types';
import { logger } from '../shared/observability/logger';
import type { Recording } from './recording';
import { getOwnerToken } from './ownerToken';

const apiBase = () => {
  if (__DEV__) {
    return Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
  }
  // Production URL would be loaded from env or config
  return 'https://api.yourdomain.com';
};

const randomId = () => {
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const defaultSetup: PracticeSetup = {
  scenario: 'Explain a technical project to a non-technical person in 60 seconds.',
  audience: 'recruiter or non-technical interviewer',
  goal: 'make the project understandable and relevant',
  requested_duration_seconds: 60,
};

export const createPracticeSession = async (setup: PracticeSetup = defaultSetup): Promise<number> => {
  const token = await getOwnerToken();
  const response = await fetch(`${apiBase()}/api/practice-sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Owner-Token': token },
    body: JSON.stringify(setup),
  });
  if (!response.ok) {
    logger.error(`Failed to create practice session (Status ${response.status})`);
    throw new Error('The backend could not create a practice session. Please try again.');
  }
  const body = await response.json();
  if (!body || typeof body.session_id !== 'number') {
    logger.error('Invalid session_id returned from API');
    throw new Error('The backend returned an invalid session. Please try again.');
  }
  return body.session_id;
};

export const analyzeRecording = async (recording: Recording, sessionId?: number | null, setup: PracticeSetup = defaultSetup): Promise<PracticeAttemptResult> => {
  // Mobile recording audio logic - we assume the Recording object already points to a valid file URI or contains the blob
  const activeSessionId = sessionId ?? await createPracticeSession(setup);
  const token = await getOwnerToken();
  
  const form = new FormData();
  form.append('audio', {
    uri: recording.audioUri,
    type: 'audio/wav',
    name: 'recording.wav'
  } as any);
  form.append('duration_seconds', String(recording.durationSeconds));
  form.append('idempotency_key', randomId());
  
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);
  try {
    const response = await fetch(`${apiBase()}/api/practice-sessions/${activeSessionId}/attempts`, {
      method: 'POST',
      headers: { 
        'X-Owner-Token': token,
        'Content-Type': 'multipart/form-data',
      },
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
    logger.error(error instanceof Error ? error.message : String(error), { audioUri: recording.audioUri, sessionId: activeSessionId });
    throw error;
  } finally { clearTimeout(timeout); }
};

export const fetchPracticeSessionHistory = async (sessionId: number): Promise<PracticeAttemptHistory> => {
  const token = await getOwnerToken();
  const response = await fetch(`${apiBase()}/api/practice-sessions/${sessionId}/attempts`, {
    method: 'GET',
    headers: { 'X-Owner-Token': token },
  });
  if (!response.ok) {
    logger.error(`Failed to load session history (Status ${response.status})`, { sessionId });
    throw new Error('The backend could not load this session history.');
  }
  try { return parsePracticeAttemptHistory(await response.json()); }
  catch { throw new Error('The backend returned invalid session history.'); }
};
