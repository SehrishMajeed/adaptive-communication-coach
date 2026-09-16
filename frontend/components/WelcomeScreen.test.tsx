import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import WelcomeScreen from './WelcomeScreen';

it('collects explicit scenario audience and goal before recording starts', () => {
  const onStart = vi.fn();
  render(<WelcomeScreen onStart={onStart} />);

  fireEvent.change(screen.getByLabelText('Scenario'), { target: { value: 'Explain my AI coaching app.' } });
  fireEvent.change(screen.getByLabelText('Audience'), { target: { value: 'scholarship professor' } });
  fireEvent.change(screen.getByLabelText('Goal'), { target: { value: 'show practical AI engineering' } });
  fireEvent.click(screen.getByText('Practice My Explanation'));

  expect(onStart).toHaveBeenCalledWith({
    scenario: 'Explain my AI coaching app.',
    audience: 'scholarship professor',
    goal: 'show practical AI engineering',
    requested_duration_seconds: 60,
  });
});
