import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import contract from '../../tests/fixtures/attempt-response.json';
import { parseFeedback } from '../types';
import FeedbackScreen from './FeedbackScreen';
import ReviewScreen from './ReviewScreen';

it('renders the exact HTTP contract checked by backend tests', () => {
  render(<FeedbackScreen feedback={parseFeedback(contract)} onRetrySame={vi.fn()} onRestart={vi.fn()} />);
  expect(screen.getByText('Clear introduction')).toBeInTheDocument();
  expect(screen.getByText('Audience adaptation')).toBeInTheDocument();
  expect(screen.queryByText('Confidence')).not.toBeInTheDocument();
  expect(screen.queryByText('Engagement')).not.toBeInTheDocument();
  expect(screen.getByText('Evidence from your transcript')).toBeInTheDocument();
  expect(screen.getByText('Um, hello.')).toBeInTheDocument();
  expect(screen.getByText(/Prompt: evaluation-audio-v2/)).toBeInTheDocument();
  expect(screen.getByText(contract.evaluation.transcript)).toBeInTheDocument();
});

it('shows backend-owned retry comparison without claiming long-term profile progress', () => {
  const currentFeedback = parseFeedback(contract);

  render(<FeedbackScreen feedback={currentFeedback} comparison={{
    comparison_id: 1,
    baseline_attempt_id: 1,
    retry_attempt_id: 2,
    intervention_id: 1,
    target_skill: 'clarity',
    comparability_status: 'comparable',
    verdict: 'improved',
    deltas: { clarity: 2, wpm: 12, total_fillers: -2 },
  }} onRetrySame={vi.fn()} onRestart={vi.fn()} />);

  expect(screen.getByText('Compared with your previous try')).toBeInTheDocument();
  expect(screen.getByText('Backend-owned retry comparison for this practice session. This is not a long-term profile update yet.')).toBeInTheDocument();
  expect(screen.getByText(/Verdict:/)).toHaveTextContent('improved');
  expect(screen.getByText('+12 wpm')).toBeInTheDocument();
  expect(screen.getByText('-2')).toBeInTheDocument();
  expect(screen.getByText('Start Over')).toBeInTheDocument();
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
  fireEvent.click(screen.getByText('Presence Review (Local Video)'));
  expect(container.querySelector('video')?.muted).toBe(true);
  fireEvent.click(screen.getByText('Voice Review (Audio Only)'));
  expect(container.querySelector('audio')).not.toBeNull();
  fireEvent.click(screen.getByText('Full Replay'));
  expect(container.querySelector('video')?.muted).toBe(false);
  fireEvent.click(screen.getByText('Find My One Priority'));
  expect(retry).toHaveBeenCalledOnce();
  unmount();
  expect(revoke).toHaveBeenCalledWith('blob:local');
  pause.mockRestore(); vi.unstubAllGlobals();
});
