
import React from 'react';
import { AIFeedback } from '../types';

interface FeedbackScreenProps {
  feedback: AIFeedback;
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

const FeedbackSection: React.FC<{ title: string; items: string[]; icon: JSX.Element; positive?: boolean }> = ({ title, items, icon, positive = true }) => {
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
}

const FeedbackScreen: React.FC<FeedbackScreenProps> = ({ feedback, onRestart }) => {
  return (
    <div className="w-full p-6 bg-gray-800/50 rounded-2xl shadow-2xl border border-gray-700 backdrop-blur-sm animate-fade-in">
      <h2 className="text-3xl font-bold text-center mb-2">Your AI Feedback</h2>
      <p className="text-lg text-center text-gray-400 mb-6">{feedback.overallImpression}</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <ScoreCircle score={feedback.confidenceScore} label="Confidence" />
        <ScoreCircle score={feedback.clarityScore} label="Clarity" />
        <ScoreCircle score={feedback.engagementScore} label="Engagement" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <FeedbackSection title="Strengths" items={[...feedback.strengths.bodyLanguage, ...feedback.strengths.vocalVariety, ...feedback.strengths.content]} icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-green-400"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>} positive />
        <FeedbackSection title="Areas for Improvement" items={[...feedback.areasForImprovement.bodyLanguage, ...feedback.areasForImprovement.vocalVariety, ...feedback.areasForImprovement.content]} icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400"><path d="m18 6-12 12"/><path d="m6 6 12 12"/></svg>} positive={false} />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {feedback.fillerWords && feedback.fillerWords.length > 0 && (
             <div className="bg-gray-700/50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Filler Words Detected</h3>
                <div className="flex flex-wrap gap-2">
                    {feedback.fillerWords.map(fw => <span key={fw.word} className="bg-gray-600 px-2 py-1 rounded text-sm">{fw.word} ({fw.count})</span>)}
                </div>
            </div>
          )}
           <div className="bg-gray-700/50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Pacing</h3>
                <p><span className="font-bold text-lg">{feedback.pace.wpm}</span> Words/Min</p>
                <p className="text-gray-400 text-sm">{feedback.pace.feedback}</p>
            </div>
      </div>


      <div className="bg-indigo-900/30 p-4 rounded-lg">
        <h3 className="flex items-center text-lg font-semibold mb-2 text-indigo-300">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            Actionable Tips for Next Time
        </h3>
        <ul className="list-disc list-inside space-y-1 text-gray-300">
          {feedback.actionableTips.map((tip, index) => <li key={index}>{tip}</li>)}
        </ul>
      </div>

      <div className="text-center mt-8">
        <button
          onClick={onRestart}
          className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-indigo-600/30"
        >
          Practice Again
        </button>
      </div>
    </div>
  );
};

export default FeedbackScreen;
