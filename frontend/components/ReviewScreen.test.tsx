import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import ReviewScreen from './ReviewScreen';
import { PracticeSetup } from '../types';

describe('ReviewScreen', () => {
  const mockVideoBlob = new Blob(['dummy video'], { type: 'video/webm' });
  const mockSetup: PracticeSetup = {
    scenario: 'Test Scenario',
    audience: 'Test Audience',
    goal: 'Test Goal',
    requested_duration_seconds: 60,
  };

  beforeEach(() => {
    // Mock URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  it('renders the video and buttons', () => {
    render(<ReviewScreen videoBlob={mockVideoBlob} onAnalyze={vi.fn()} onRestart={vi.fn()} error={null} />);
    expect(screen.getByText('Review Before AI Feedback')).toBeInTheDocument();
    expect(screen.getByText('Record Again')).toBeInTheDocument();
    expect(screen.getByText('Find My One Priority')).toBeInTheDocument();
  });

  it('renders the PracticeContextCard when setup is provided', () => {
    render(<ReviewScreen setup={mockSetup} videoBlob={mockVideoBlob} onAnalyze={vi.fn()} onRestart={vi.fn()} error={null} />);
    expect(screen.getByText('Practice context')).toBeInTheDocument();
    expect(screen.getByText('Test Scenario')).toBeInTheDocument();
    expect(screen.getByText('Test Audience')).toBeInTheDocument();
    expect(screen.getByText('Test Goal')).toBeInTheDocument();
  });

  it('calls onAnalyze when the analyze button is clicked', () => {
    const onAnalyze = vi.fn();
    render(<ReviewScreen videoBlob={mockVideoBlob} onAnalyze={onAnalyze} onRestart={vi.fn()} error={null} />);
    fireEvent.click(screen.getByText('Find My One Priority'));
    expect(onAnalyze).toHaveBeenCalledTimes(1);
  });

  it('calls onRestart when the restart button is clicked', () => {
    const onRestart = vi.fn();
    render(<ReviewScreen videoBlob={mockVideoBlob} onAnalyze={vi.fn()} onRestart={onRestart} error={null} />);
    fireEvent.click(screen.getByText('Record Again'));
    expect(onRestart).toHaveBeenCalledTimes(1);
  });

  it('displays an error message when error prop is provided', () => {
    render(<ReviewScreen videoBlob={mockVideoBlob} onAnalyze={vi.fn()} onRestart={vi.fn()} error="Network failed" />);
    expect(screen.getByText('Network failed')).toBeInTheDocument();
  });
});
