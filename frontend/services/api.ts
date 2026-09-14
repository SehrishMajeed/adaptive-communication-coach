import { AIFeedback, parseFeedback } from '../types';
import { prepareAudio } from './audio';
import type { Recording } from './recording';

export const analyzeRecording = async (recording: Recording): Promise<AIFeedback> => {
  let audio: Blob;
  try { audio = await prepareAudio(recording.audioBlob); }
  catch { throw new Error('Audio could not be prepared. You can review this recording or record again in another browser.'); }
  const form = new FormData();
  form.append('audio', audio, 'recording.wav');
  form.append('duration_seconds', String(recording.durationSeconds));
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60_000);
  try {
    const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${base}/api/sessions/latest/attempts`, { method: 'POST', body: form, signal: controller.signal });
    if (!response.ok) {
      if (response.status === 422 || response.status === 413) throw new Error('The recording was rejected. Record 1–60 seconds and try again.');
      if (response.status === 502) throw new Error('The evaluator could not process this recording. Please try again.');
      throw new Error('The backend could not save or process the recording. Please try again.');
    }
    try { return parseFeedback(await response.json()); }
    catch { throw new Error('The backend returned an invalid result. Please try again.'); }
  } catch (error) {
    if (controller.signal.aborted || error instanceof TypeError) {
      throw new Error('The request could not finish. Check your connection and try again.');
    }
    throw error;
  } finally { clearTimeout(timeout); }
};
