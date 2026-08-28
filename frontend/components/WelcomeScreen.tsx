
import React from 'react';

interface WelcomeScreenProps {
  onStart: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart }) => {
  return (
    <div className="text-center p-8 bg-gray-800/50 rounded-2xl shadow-2xl border border-gray-700 backdrop-blur-sm">
      <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-500 mb-4">
        Master Your Soft Skills
      </h2>
      <p className="max-w-2xl mx-auto text-lg text-gray-300 mb-8">
        Aura helps you become a more confident and effective communicator. Record a short practice session, review your performance, and get instant, personalized feedback from our AI coach.
      </p>
      <button
        onClick={onStart}
        className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-indigo-600/30"
      >
        Start Practice Session
      </button>
    </div>
  );
};

export default WelcomeScreen;
