import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { startCapture } from './recording';

export class FakeRecorder {
  static instances: FakeRecorder[] = [];
  static isTypeSupported = () => true;
  state = 'inactive';
  ondataavailable: ((e: { data: Blob }) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: (() => void) | null = null;
  start = vi.fn(() => { this.state = 'recording'; });
  stop = vi.fn(() => {
    this.state = 'inactive';
    this.ondataavailable?.({ data: new Blob(['audio-or-video']) });
    this.onstop?.();
  });
  mimeType: string;
  constructor(public stream: MediaStream, options: { mimeType: string }) {
    this.mimeType = options.mimeType;
    FakeRecorder.instances.push(this);
  }
}
export const makeStream = () => {
  const audio = { kind: 'audio', stop: vi.fn() };
  const video = { kind: 'video', stop: vi.fn() };
  return { getTracks: () => [audio, video], getAudioTracks: () => [audio] } as unknown as MediaStream;
};
export function installMedia() {
  FakeRecorder.instances = [];
  vi.stubGlobal('MediaRecorder', FakeRecorder);
  vi.stubGlobal('MediaStream', class {
    constructor(private tracks: MediaStreamTrack[]) {}
    getTracks() { return this.tracks; }
    getAudioTracks() { return this.tracks.filter(track => track.kind === 'audio'); }
  });
}

describe('capture resource ownership', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'performance'] });
    installMedia();
  });
  afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

  it('manual stop is idempotent and separates audio from local video', () => {
    const media = makeStream(); const complete = vi.fn(); const failed = vi.fn();
    const capture = startCapture(media, complete, failed, vi.fn());
    expect(FakeRecorder.instances[1].stream.getTracks().map(x => x.kind)).toEqual(['audio']);
    vi.advanceTimersByTime(5000);
    capture.stop(); capture.stop();
    expect(complete).toHaveBeenCalledTimes(1);
    expect(complete.mock.calls[0][0].durationSeconds).toBe(5);
    expect(complete.mock.calls[0][0].audioBlob.type).toMatch(/^audio/);
    for (const recorder of FakeRecorder.instances) {
      expect(recorder.start).toHaveBeenCalledTimes(1);
      expect(recorder.stop).toHaveBeenCalledTimes(1);
    }
    media.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledTimes(1));
    expect(vi.getTimerCount()).toBe(0);
    expect(failed).not.toHaveBeenCalled();
  });
  it('automatically stops once at sixty seconds', () => {
    const complete = vi.fn();
    startCapture(makeStream(), complete, vi.fn(), vi.fn());
    vi.advanceTimersByTime(60_000);
    expect(complete).toHaveBeenCalledTimes(1);
    expect(complete.mock.calls[0][0].durationSeconds).toBe(60);
    expect(vi.getTimerCount()).toBe(0);
  });
  it('cancel releases everything and never completes after unmount', () => {
    const media = makeStream(); const complete = vi.fn();
    const capture = startCapture(media, complete, vi.fn(), vi.fn());
    capture.cancel(); capture.cancel();
    vi.advanceTimersByTime(65_000);
    expect(complete).not.toHaveBeenCalled();
    media.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledTimes(1));
    expect(vi.getTimerCount()).toBe(0);
  });
  it('recorder failure is recoverable and releases both recorders', () => {
    const complete = vi.fn(); const failed = vi.fn(); const media = makeStream();
    startCapture(media, complete, failed, vi.fn());
    FakeRecorder.instances[0].onerror?.();
    expect(failed).toHaveBeenCalledTimes(1);
    expect(complete).not.toHaveBeenCalled();
    expect(vi.getTimerCount()).toBe(0);
    media.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledTimes(1));
  });
});
