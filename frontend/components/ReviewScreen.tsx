
import React, { useState, useEffect, useRef } from 'react';
import { ReviewMode } from '../types';

interface ReviewScreenProps {
  videoBlob: Blob;
  onAnalyze: () => void;
  onRestart: () => void;
  error: string | null;
}

const modeConfig = {
    [ReviewMode.FULL]: { title: 'Full Replay', description: 'Watch and listen to your full performance. Note your overall delivery and message clarity.' },
    [ReviewMode.MUTED]: { title: 'Body Language Review (Muted)', description: 'Watch without sound. Focus on your posture, gestures, facial expressions, and eye contact.' },
    [ReviewMode.AUDIO_ONLY]: { title: 'Vocal Tone Review (Audio Only)', description: 'Listen without video. Focus on your tone, pace, clarity, and use of filler words.' }
};

const ReviewScreen: React.FC<ReviewScreenProps> = ({ videoBlob, onAnalyze, onRestart, error }) => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [reviewMode, setReviewMode] = useState<ReviewMode>(ReviewMode.FULL);
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const url = URL.createObjectURL(videoBlob);
    setVideoUrl(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [videoBlob]);

  const handleModeChange = (mode: ReviewMode) => {
    setReviewMode(mode);
    videoRef.current?.pause();
    audioRef.current?.pause();
  };

  return (
    <div className="w-full flex flex-col items-center">
      <h2 className="text-3xl font-bold mb-4">Review Your Performance</h2>
      <p className="text-gray-400 mb-6">Use the modes below to analyze your practice session from different perspectives.</p>

      <div className="w-full max-w-2xl flex flex-col md:flex-row gap-6">
        <div className="flex-grow">
          <div className="w-full aspect-video bg-gray-950 rounded-lg overflow-hidden shadow-2xl border border-gray-700">
            {videoUrl && (
              <>
                <video
                  ref={videoRef}
                  key={videoUrl}
                  src={videoUrl}
                  controls
                  muted={reviewMode === ReviewMode.MUTED}
                  className={reviewMode === ReviewMode.AUDIO_ONLY ? 'hidden' : 'w-full h-full'}
                />
                {reviewMode === ReviewMode.AUDIO_ONLY && (
                  <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-gray-800">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-indigo-400 mb-4"><path d="M12 2a3.5 3.5 0 0 0-3.5 3.5v9a3.5 3.5 0 0 0 7 0v-9A3.5 3.5 0 0 0 12 2Z"/><path d="M17 10v2a5 5 0 0 1-10 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
                    <h3 className="text-lg font-semibold">Audio Only Mode</h3>
                     <audio ref={audioRef} key={`audio-${videoUrl}`} src={videoUrl} controls className="w-full mt-4" />
                  </div>
                )}
              </>
            )}
          </div>
        </div>
        <div className="md:w-64 flex-shrink-0 flex md:flex-col gap-2">
            {Object.values(ReviewMode).map(mode => (
                <button
                    key={mode}
                    onClick={() => handleModeChange(mode)}
                    className={`w-full p-3 text-left rounded-lg transition-colors ${reviewMode === mode ? 'bg-indigo-600 text-white' : 'bg-gray-800 hover:bg-gray-700'}`}
                >
                   <span className="font-bold">{modeConfig[mode].title}</span>
                </button>
            ))}
        </div>
      </div>
      <div className="mt-4 p-4 bg-gray-800 rounded-lg text-center max-w-2xl">
        <p className="text-gray-300">{modeConfig[reviewMode].description}</p>
      </div>

      {error && <div role="alert" className="mt-4 p-4 bg-red-900/50 text-red-300 rounded-lg max-w-2xl w-full text-center">{error}</div>}

      <div className="mt-8 flex items-center space-x-4">
        <button onClick={onRestart} className="px-6 py-3 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 transition-colors">
            Record Again
        </button>
        <button onClick={onAnalyze} className="px-8 py-4 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-purple-600/30">
            Get AI Feedback
        </button>
      </div>
    </div>
  );
};

export default ReviewScreen;
