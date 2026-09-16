import React from 'react';
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import PracticeContextCard from './PracticeContextCard';

const setup = {
  scenario: 'Explain the AI coaching architecture.',
  audience: 'scholarship professor',
  goal: 'show practical AI engineering judgment',
  requested_duration_seconds: 60,
};

it('renders the selected scenario, audience, goal and target duration', () => {
  render(<PracticeContextCard setup={setup} />);

  expect(screen.getByLabelText('Practice context')).toBeInTheDocument();
  expect(screen.getByText(setup.scenario)).toBeInTheDocument();
  expect(screen.getByText(setup.audience)).toBeInTheDocument();
  expect(screen.getByText(setup.goal)).toBeInTheDocument();
  expect(screen.getByText('Target: 60s')).toBeInTheDocument();
});

it('renders nothing until setup exists', () => {
  const { container } = render(<PracticeContextCard setup={null} />);

  expect(container).toBeEmptyDOMElement();
});
