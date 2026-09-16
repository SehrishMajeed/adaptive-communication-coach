import React from 'react';
import { AIFeedback, BackendComparison } from '../types';

interface FeedbackScreenProps {
  feedback: AIFeedback;
  comparison?: BackendComparison | null;
  onRetrySame: () => void;
  onRestart: () => void;
}

const ScoreCircle: React.FC<{ score: number; label: string }> = ({ score, label }) => {
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;
  const colorClass = score > 75 ? 'text-green-400' : score > 50 ? 'text-yellow-400' : 'text-red-400';

  return (
    <div className="flex flex-col items-center text-center">
      <div className="relative w-32 h-32">
        <svg className="w-full h-full" viewBox="0 0 100 100">
          <circle className="text-gray-700" strokeWidth="5" stroke="currentColor" fill="transparent" r="45" cx="50" cy="50" />
          <circle
            className={colorClass}
            strokeWidth="5"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            stroke="currentColor"
            fill="transparent"
            r="45"
            cx="50"
            cy="50"
            transform="rotate(-90 50 50)"
          />
          <text x="50" y="50" className={`fill-current ${colorClass} text-3xl font-bold`} textAnchor="middle" dominantBaseline="middle">{score}</text>
        </svg>
      </div>
      <p className="mt-2 text-sm font-semibold text-gray-300">{label}</p>
    </div>
  );
};

const FeedbackSection: React.FC<{ title: string; items: string[]; icon: React.ReactElement; positive?: boolean }> = ({ title, items, icon, positive = true }) => {
  if (!items || items.length === 0) return null;
  return (
    <div className={`p-4 rounded-lg ${positive ? 'bg-green-900/30' : 'bg-red-900/30'}`}>
      <h3 className="flex items-center text-lg font-semibold mb-2">
        {icon}
        <span className="ml-2">{title}</span>
      </h3>
      <ul className="list-disc list-inside space-y-1 text-gray-300">
        {items.map((item, index) => <li key={index}>{item}</li>)}
      </ul>
    </div>
  );
};

const focusDrills: Record<string, string> = {
  clarity: 'Say the main idea in one plain sentence before adding details.',
  structure: 'Use this order: problem, what you built, result, why it matters.',
  conciseness: 'Cut one side detail and keep only what helps the listener decide.',
  audience_awareness: 'Replace one technical term with the listener-facing benefit.',
};

const formatDelta = (delta: number, unit = '') => {
  const rounded = Math.round(delta * 10) / 10;
  return `${rounded > 0 ? '+' : ''}${rounded}${unit}`;
};

const ComparisonMetric: React.FC<{ label: string; delta: number; unit?: string }> = ({ label, delta, unit = '' }) => (
  <div className="bg-gray-700/50 p-4 rounded-lg">
    <p className="text-sm text-gray-400">{label}</p>
    <p className="text-2xl font-bold text-white">{formatDelta(delta, unit)}</p>
  </div>
);

const FeedbackScreen: React.FC<FeedbackScreenProps> = ({ feedback, comparison, onRetrySame, onRestart }) => {
  const primaryFocus = feedback.evaluation.recommended_focus[0];
  const drill = primaryFocus ? focusDrills[primaryFocus] : 'Retry the explanation with a clearer opening sentence.';
  const backendDeltas = comparison?.deltas ?? {};
  const completed = feedback.evaluation.evaluator_status === 'completed';

  return (
    <div className="w-full p-6 bg-gray-800/50 rounded-2xl shadow-2xl border border-gray-700 backdrop-blur-sm animate-fade-in">
      <h2 className="text-3xl font-bold text-center mb-2">Your One Practice Target</h2>
      <p className="text-lg text-center text-gray-400 mb-6">AI suggestions for this attempt — not verified progress.</p>

      {completed ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <ScoreCircle score={feedback.evaluation.clarity! * 10} label="Clarity" />
          <ScoreCircle score={feedback.evaluation.structure! * 10} label="Structure" />
          <ScoreCircle score={feedback.evaluation.conciseness! * 10} label="Conciseness" />
          <ScoreCircle score={feedback.evaluation.audience_awareness! * 10} label="Audience adaptation" />
        </div>
      ) : (
        <div className="mb-6 bg-yellow-900/30 border border-yellow-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-yellow-200">Evaluator abstained</h3>
          <p className="text-gray-300">{feedback.evaluation.abstention_reason}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <FeedbackSection title="Strengths" items={feedback.evaluation.strengths} icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>} positive />
        <FeedbackSection title="Areas for Improvement" items={feedback.evaluation.weaknesses} icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400"><path d="m18 6-12 12" /><path d="m6 6 12 12" /></svg>} positive={false} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {feedback.measurements.filler_words_list && feedback.measurements.filler_words_list.length > 0 && (
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <h3 className="font-semibold mb-2">Filler candidates in transcript</h3>
            <div className="flex flex-wrap gap-2">
              {feedback.measurements.filler_words_list.map((fillerWord) => <span key={fillerWord.word} className="bg-gray-600 px-2 py-1 rounded text-sm">{fillerWord.word} ({fillerWord.count})</span>)}
            </div>
          </div>
        )}
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">Pacing</h3>
          <p><span className="font-bold text-lg">{feedback.measurements.wpm}</span> Words/Min</p>
          <p className="text-gray-400 text-sm">Counts depend on transcription accuracy.</p>
        </div>
      </div>

      {completed && (
        <div className="bg-indigo-900/30 p-4 rounded-lg">
          <h3 className="flex items-center text-lg font-semibold mb-2 text-indigo-300">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
            Suggested focus and retry drill
          </h3>
          <p className="text-gray-300">
            Focus on <span className="font-semibold">{primaryFocus ? primaryFocus.replaceAll('_', ' ') : 'clarity'}</span>. {drill}
          </p>
          <p className="mt-2 text-sm text-gray-400">This is a practice suggestion, not proof of skill improvement. Record again to compare honestly.</p>
        </div>
      )}

      {feedback.evaluation.evidence.length > 0 && (
        <div className="mt-6 bg-gray-900/60 p-4 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-2">Evidence from your transcript</h3>
          <div className="space-y-3">
            {feedback.evaluation.evidence.map((item, index) => (
              <div key={`${item.skill}-${index}`} className="bg-gray-700/50 p-3 rounded-lg">
                <p className="text-sm text-indigo-200 font-semibold">{item.skill.replaceAll('_', ' ')}</p>
                <blockquote className="text-gray-200 border-l-2 border-indigo-400 pl-3 my-2">{item.quote}</blockquote>
                <p className="text-sm text-gray-400">{item.note}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {comparison && (
        <div className="mt-6 bg-gray-900/60 p-4 rounded-lg border border-gray-700">
          <h3 className="text-lg font-semibold mb-1">Compared with your previous try</h3>
          <p className="text-sm text-gray-400 mb-4">Backend-owned retry comparison for this practice session. This is not a long-term profile update yet.</p>
          <p className="text-sm text-gray-300 mb-4">
            Target: <span className="font-semibold">{comparison.target_skill.replaceAll('_', ' ')}</span>. Verdict: <span className="font-semibold">{comparison.verdict.replaceAll('_', ' ')}</span>.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'clarity') && <ComparisonMetric label="Clarity" delta={backendDeltas.clarity} unit=" pts" />}
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'structure') && <ComparisonMetric label="Structure" delta={backendDeltas.structure} unit=" pts" />}
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'conciseness') && <ComparisonMetric label="Conciseness" delta={backendDeltas.conciseness} unit=" pts" />}
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'audience_awareness') && <ComparisonMetric label="Audience adaptation" delta={backendDeltas.audience_awareness} unit=" pts" />}
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'wpm') && <ComparisonMetric label="Pace change" delta={backendDeltas.wpm} unit=" wpm" />}
            {Object.prototype.hasOwnProperty.call(backendDeltas, 'total_fillers') && <ComparisonMetric label="Filler candidate change" delta={backendDeltas.total_fillers} />}
          </div>
        </div>
      )}

      <p className="mt-4 text-sm text-gray-400">Audio duration: {feedback.measurements.duration_seconds.toFixed(1)}s (decoded sample frames). Words: {feedback.measurements.word_count}. Filler candidates: {feedback.measurements.total_fillers}.</p>
      <p className="mt-2 text-sm text-gray-500">Prompt: {feedback.provenance.prompt_version}. Model: {feedback.provenance.model_id}. Rubric: {feedback.provenance.rubric_version}.</p>
      <details className="mt-4"><summary>Transcript used for these measurements</summary><p className="mt-2 whitespace-pre-wrap">{feedback.evaluation.transcript}</p></details>
      <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
        <button
          onClick={onRetrySame}
          className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-indigo-600/30"
        >
          Retry Same Explanation
        </button>
        <button
          onClick={onRestart}
          className="px-8 py-4 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 transition-all duration-300"
        >
          Start Over
        </button>
      </div>
    </div>
  );
};

export default FeedbackScreen;
