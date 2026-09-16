
import React, { useState, useCallback } from 'react';
import { AppState, AIFeedback, BackendComparison, BackendWorkflow, PracticeAttemptResult, PracticeSetup } from './types';
import WelcomeScreen from './components/WelcomeScreen';
import RecordingScreen from './components/RecordingScreen';
import ReviewScreen from './components/ReviewScreen';
import FeedbackScreen from './components/FeedbackScreen';
import Loader from './components/Loader';
import { analyzeRecording, fetchPracticeSessionHistory } from './services/api';
import type { Recording } from './services/recording';

const App: React.FC = () => {
  const [appState, setAppState] = useState<AppState>(AppState.WELCOME);
  const [recording, setRecording] = useState<Recording | null>(null);
  const [feedback, setFeedback] = useState<AIFeedback | null>(null);
  const [comparison, setComparison] = useState<BackendComparison | null>(null);
  const [workflow, setWorkflow] = useState<BackendWorkflow | null>(null);
  const [history, setHistory] = useState<PracticeAttemptResult[]>([]);
  const [setup, setSetup] = useState<PracticeSetup | null>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStart = (selectedSetup: PracticeSetup) => {
    setSetup(selectedSetup);
    setAppState(AppState.RECORDING);
  };

  const handleRecordingComplete = (result: Recording) => {
    setRecording(result);
    setAppState(AppState.REVIEW);
  };

  const handleAnalysis = useCallback(async () => {
    if (!recording) return;

    setAppState(AppState.ANALYZING);
    setError(null);

    try {
      const result = await analyzeRecording(recording, sessionId, setup ?? undefined);
      setSessionId(result.sessionId);
      setComparison(result.comparison);
      setWorkflow(result.workflow);
      setFeedback(result.feedback);
      setHistory([result]);
      fetchPracticeSessionHistory(result.sessionId)
        .then((loaded) => setHistory(loaded.attempts))
        .catch(() => setHistory([result]));
      setAppState(AppState.FEEDBACK);
    } catch (err) {

      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
      setError(`Failed to get AI feedback. ${errorMessage}`);
      setAppState(AppState.REVIEW); // Go back to review screen on error
    }
  }, [recording, sessionId, setup]);

  const handleRetrySameExplanation = () => {
    setRecording(null);
    setError(null);
    setAppState(AppState.RECORDING);
  };

  const handleRestart = () => {
    setAppState(AppState.WELCOME);
    setRecording(null);
    setFeedback(null);
    setComparison(null);
    setWorkflow(null);
    setHistory([]);
    setSetup(null);
    setSessionId(null);
    setError(null);
  };

  const renderContent = () => {
    switch (appState) {
      case AppState.WELCOME:
        return <WelcomeScreen onStart={handleStart} />;
      case AppState.RECORDING:
        return <RecordingScreen onRecordingComplete={handleRecordingComplete} />;
      case AppState.REVIEW:
        return <ReviewScreen videoBlob={recording!.videoBlob} onAnalyze={handleAnalysis} error={error} onRestart={handleRestart} />;
      case AppState.ANALYZING:
        return <Loader />;
      case AppState.FEEDBACK:
        return <FeedbackScreen feedback={feedback!} workflow={workflow} comparison={comparison} history={history} onRetrySame={handleRetrySameExplanation} onRestart={handleRestart} />;
      default:
        return <WelcomeScreen onStart={handleStart} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans flex flex-col items-center justify-center p-4">
        <header className="absolute top-0 left-0 p-6 flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-tr from-purple-500 to-indigo-600 rounded-full flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M12 22a6.955 6.955 0 0 1-7-7c0-4 7-11 7-11s7 7 7 11a6.955 6.955 0 0 1-7 7Z"/><path d="M12 11a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/></svg>
            </div>
            <h1 className="text-2xl font-bold tracking-tight">Aura Coach</h1>
        </header>
        <main className="w-full max-w-4xl">
            {renderContent()}
        </main>
    </div>
  );
};

export default App;
