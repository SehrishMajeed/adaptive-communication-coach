import React, { StrictMode } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import RecordingScreen from './RecordingScreen';

const setup = {
  scenario: 'Explain the AI coaching architecture.',
  audience: 'scholarship professor',
  goal: 'show practical AI engineering judgment',
  requested_duration_seconds: 60,
};

const stream = () => {
  const tracks = [{ kind: 'audio', stop: vi.fn() }, { kind: 'video', stop: vi.fn() }];
  return { getTracks: () => tracks, getAudioTracks: () => [tracks[0]] } as unknown as MediaStream;
};
beforeEach(() => {
  vi.stubGlobal('MediaRecorder', class {
    static isTypeSupported = () => true;
    state = 'inactive'; mimeType: string;
    onstop: (() => void) | null = null;
    onerror: (() => void) | null = null;
    ondataavailable: ((e: { data: Blob }) => void) | null = null;
    constructor(_stream: MediaStream, options: { mimeType: string }) { this.mimeType = options.mimeType; }
    start() { this.state = 'recording'; }
    stop() { this.state = 'inactive'; this.ondataavailable?.({ data: new Blob(['media']) }); this.onstop?.(); }
  });
  vi.stubGlobal('MediaStream', class { constructor(public tracks: MediaStreamTrack[]) {} });
});
afterEach(() => { vi.unstubAllGlobals(); });

it('late permission results are released after unmount', async () => {
  const media = stream();
  let resolve!: (value: MediaStream) => void;
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: () => new Promise<MediaStream>(r => { resolve = r; }) } });
  const view = render(<RecordingScreen onRecordingComplete={vi.fn()} />);
  view.unmount();
  await act(async () => resolve(media));
  media.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledOnce());
});

it('StrictMode releases the abandoned acquisition and retains only the current stream', async () => {
  const first = stream(); const second = stream();
  const acquire = vi.fn().mockResolvedValueOnce(first).mockResolvedValueOnce(second);
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: acquire } });
  const view = render(<StrictMode><RecordingScreen onRecordingComplete={vi.fn()} /></StrictMode>);
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
  first.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledOnce());
  second.getTracks().forEach(track => expect(track.stop).not.toHaveBeenCalled());
  view.unmount();
  second.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledOnce());
});

it('permission failure offers a working retry', async () => {
  const acquire = vi.fn().mockRejectedValueOnce(new Error('private')).mockResolvedValueOnce(stream());
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: acquire } });
  render(<RecordingScreen onRecordingComplete={vi.fn()} />);
  await screen.findByRole('alert');
  expect(screen.queryByText('private')).not.toBeInTheDocument();
  fireEvent.click(screen.getByText('Try Again'));
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
});

it('keeps the selected setup visible while recording', async () => {
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: vi.fn().mockResolvedValue(stream()) } });
  render(<RecordingScreen setup={setup} onRecordingComplete={vi.fn()} />);
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
  expect(screen.getByText(setup.scenario)).toBeInTheDocument();
  expect(screen.getByText(setup.audience)).toBeInTheDocument();
  expect(screen.getByText(setup.goal)).toBeInTheDocument();
  expect(screen.getByText('Record for the selected 60-second target.')).toBeInTheDocument();
});

it('active unmount cancels capture, clears timers and releases tracks', async () => {
  const media = stream();
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: vi.fn().mockResolvedValue(media) } });
  const complete = vi.fn();
  const view = render(<RecordingScreen onRecordingComplete={complete} />);
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
  vi.useFakeTimers();
  fireEvent.click(screen.getByText('Start Recording'));
  view.unmount();
  expect(vi.getTimerCount()).toBe(0);
  expect(complete).not.toHaveBeenCalled();
  media.getTracks().forEach(track => expect(track.stop).toHaveBeenCalledOnce());
  vi.useRealTimers();
});

it('a fresh recording can start after the previous screen unmounts', async () => {
  const acquire = vi.fn().mockImplementation(async () => stream());
  vi.stubGlobal('navigator', { mediaDevices: { getUserMedia: acquire } });
  const first = render(<RecordingScreen onRecordingComplete={vi.fn()} />);
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
  fireEvent.click(screen.getByText('Start Recording'));
  first.unmount();
  const second = render(<RecordingScreen onRecordingComplete={vi.fn()} />);
  await waitFor(() => expect(screen.getByText('Start Recording')).toBeEnabled());
  fireEvent.click(screen.getByText('Start Recording'));
  expect(screen.getByText('Stop Recording')).toBeInTheDocument();
  second.unmount();
});
