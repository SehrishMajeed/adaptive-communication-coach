
import React from 'react';
import { PracticeSetup } from '../types';

interface WelcomeScreenProps {
  onStart: (setup: PracticeSetup) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart }) => {
  const [scenario, setScenario] = React.useState('Explain a technical project to a non-technical person in 60 seconds.');
  const [audience, setAudience] = React.useState('recruiter or non-technical interviewer');
  const [goal, setGoal] = React.useState('make the project understandable and relevant');
  const setup = {
    scenario,
    audience,
    goal,
    requested_duration_seconds: 60,
  };

  return (
    <div className="p-8 bg-gray-800/50 rounded-2xl shadow-2xl border border-gray-700 backdrop-blur-sm">
      <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-500 mb-4">
        Make Your Technical Explanation Land
      </h2>
      <p className="max-w-2xl text-lg text-gray-300 mb-6">
        Set the speaking context first, then practice one 60-second explanation. Video stays local; the backend stores the transcript, feedback, workflow route, and retry history for this session.
      </p>
      <div className="grid gap-4 text-left mb-8">
        <label className="block">
          <span className="text-sm font-semibold text-gray-300">Scenario</span>
          <textarea
            value={scenario}
            onChange={(event) => setScenario(event.target.value)}
            maxLength={500}
            rows={3}
            className="mt-2 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <label className="block">
            <span className="text-sm font-semibold text-gray-300">Audience</span>
            <input
              value={audience}
              onChange={(event) => setAudience(event.target.value)}
              maxLength={200}
              className="mt-2 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </label>
          <label className="block">
            <span className="text-sm font-semibold text-gray-300">Goal</span>
            <input
              value={goal}
              onChange={(event) => setGoal(event.target.value)}
              maxLength={300}
              className="mt-2 w-full rounded-lg bg-gray-900 border border-gray-700 p-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </label>
        </div>
      </div>
      <button
        onClick={() => onStart(setup)}
        disabled={!scenario.trim() || !audience.trim() || !goal.trim()}
        className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-indigo-600/30"
      >
        Practice My Explanation
      </button>
    </div>
  );
};

export default WelcomeScreen;
