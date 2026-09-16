import React from 'react';
import { PracticeSetup } from '../types';

interface PracticeContextCardProps {
  setup?: PracticeSetup | null;
  compact?: boolean;
}

const PracticeContextCard: React.FC<PracticeContextCardProps> = ({ setup, compact = false }) => {
  if (!setup) return null;

  return (
    <section aria-label="Practice context" className={`w-full max-w-2xl bg-gray-900/60 border border-gray-700 rounded-lg ${compact ? 'p-3' : 'p-4'}`}>
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-3">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-indigo-200">Practice context</h3>
        <p className="text-xs text-gray-400">Target: {setup.requested_duration_seconds}s</p>
      </div>
      <dl className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
        <div>
          <dt className="text-gray-400">Scenario</dt>
          <dd className="text-gray-100">{setup.scenario}</dd>
        </div>
        <div>
          <dt className="text-gray-400">Audience</dt>
          <dd className="text-gray-100">{setup.audience}</dd>
        </div>
        <div>
          <dt className="text-gray-400">Goal</dt>
          <dd className="text-gray-100">{setup.goal}</dd>
        </div>
      </dl>
    </section>
  );
};

export default PracticeContextCard;
