import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import contract from '../../tests/fixtures/attempt-response.json';
import { parseFeedback } from '../types';
import FeedbackScreen from './FeedbackScreen';
import ReviewScreen from './ReviewScreen';

it('renders the exact HTTP contract checked by backend tests', () => {
  render(<FeedbackScreen feedback={parseFeedback(contract)} onRestart={vi.fn()} />);
  expect(screen.getByText('Clear introduction')).toBeInTheDocument();
  expect(screen.getByText('Audience adaptation')).toBeInTheDocument();
  expect(screen.queryByText('Confidence')).not.toBeInTheDocument();
  expect(screen.queryByText('Engagement')).not.toBeInTheDocument();
  expect(screen.getByText(contract.evaluation.transcript)).toBeInTheDocument();
});

it('rejects malformed response values instead of rendering invented scores', () => {
  expect(() => parseFeedback({})).toThrow();
  expect(() => parseFeedback({ ...contract, evaluation: { ...contract.evaluation, clarity: 999 } })).toThrow();
  expect(() => parseFeedback({ ...contract, measurements: { ...contract.measurements, total_fillers: 9 } })).toThrow();
});

it('keeps review, retry and all three perspectives available after failure', () => {
  const revoke = vi.fn();
  vi.stubGlobal('URL', { createObjectURL: () => 'blob:local', revokeObjectURL: revoke });
  const pause = vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
  const retry = vi.fn();
  const { container, unmount } = render(<ReviewScreen videoBlob={new Blob(['local-video'])} onAnalyze={retry} onRestart={vi.fn()} error="Evaluation failed. Try again." />);
  expect(screen.getByRole('alert')).toHaveTextContent('Evaluation failed');
  fireEvent.click(screen.getByText('Body Language Review (Muted)'));
  expect(container.querySelector('video')?.muted).toBe(true);
  fireEvent.click(screen.getByText('Vocal Tone Review (Audio Only)'));
  expect(container.querySelector('audio')).not.toBeNull();
  fireEvent.click(screen.getByText('Full Replay'));
  expect(container.querySelector('video')?.muted).toBe(false);
  fireEvent.click(screen.getByText('Get AI Feedback'));
  expect(retry).toHaveBeenCalledOnce();
  unmount();
  expect(revoke).toHaveBeenCalledWith('blob:local');
  pause.mockRestore(); vi.unstubAllGlobals();
});
