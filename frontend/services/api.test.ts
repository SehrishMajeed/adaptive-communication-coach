import { afterEach, expect, it, vi } from 'vitest';
import contract from '../../tests/fixtures/attempt-response.json';
import { analyzeRecording } from './api';
import { prepareAudio } from './audio';
vi.mock('./audio', () => ({ prepareAudio: vi.fn() }));
const recording = { videoBlob: new Blob(['secret-video']), audioBlob: new Blob(['audio']), durationSeconds: 5 };
afterEach(() => { vi.unstubAllGlobals(); vi.resetAllMocks(); });

it('posts only prepared audio and explicit duration, never local video', async () => {
  vi.mocked(prepareAudio).mockResolvedValue(new Blob(['pcm'], { type: 'audio/wav' }));
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => contract });
  vi.stubGlobal('fetch', fetch);
  expect(await analyzeRecording(recording)).toEqual(contract);
  expect(prepareAudio).toHaveBeenCalledWith(recording.audioBlob);
  const form = fetch.mock.calls[0][1].body as FormData;
  expect([...form.keys()]).toEqual(['audio', 'duration_seconds']);
  expect((form.get('audio') as File).type).toBe('audio/wav');
  expect(form.get('duration_seconds')).toBe('5');
});

it.each([422, 502, 503])('returns a recoverable error for HTTP %s', async status => {
  vi.mocked(prepareAudio).mockResolvedValue(new Blob(['pcm']));
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status }));
  await expect(analyzeRecording(recording)).rejects.toThrow(/try again/i);
});

it('rejects network failures and invalid successful responses', async () => {
  vi.mocked(prepareAudio).mockResolvedValue(new Blob(['pcm']));
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('private-network-detail')));
  await expect(analyzeRecording(recording)).rejects.toThrow('Check your connection');
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }));
  await expect(analyzeRecording(recording)).rejects.toThrow('invalid result');
});

it('conversion failure does not upload anything', async () => {
  vi.mocked(prepareAudio).mockRejectedValue(new Error('codec'));
  const fetch = vi.fn(); vi.stubGlobal('fetch', fetch);
  await expect(analyzeRecording(recording)).rejects.toThrow('Audio could not be prepared');
  expect(fetch).not.toHaveBeenCalled();
});

it('aborts stalled requests with a recoverable timeout', async () => {
  vi.useFakeTimers();
  vi.mocked(prepareAudio).mockResolvedValue(new Blob(['pcm']));
  vi.stubGlobal('fetch', vi.fn((_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')));
  })));
  const result = expect(analyzeRecording(recording)).rejects.toThrow('Check your connection');
  await vi.advanceTimersByTimeAsync(60_000);
  await result;
  expect(vi.getTimerCount()).toBe(0);
  vi.useRealTimers();
});
