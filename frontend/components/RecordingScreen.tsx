import React, { useEffect, useRef, useState } from 'react';
import { Recording, startCapture } from '../services/recording';
import { PracticeSetup } from '../types';
import PracticeContextCard from './PracticeContextCard';

interface RecordingScreenProps {
  setup?: PracticeSetup | null;
  onRecordingComplete: (recording: Recording) => void;
}

const RecordingScreen: React.FC<RecordingScreenProps> = ({ setup, onRecordingComplete }) => {
  const [stage, setStage] = useState<'loading' | 'ready' | 'recording' | 'stopping' | 'error'>('loading');
  const [remaining, setRemaining] = useState(60);
  const [retry, setRetry] = useState(0);
  const stream = useRef<MediaStream | null>(null);
  const capture = useRef<ReturnType<typeof startCapture> | null>(null);
  const video = useRef<HTMLVideoElement>(null);
  const alive = useRef(false);

  useEffect(() => {
    let cancelled = false;
    alive.current = true;
    setStage('loading');
    const acquire = async () => {
      try {
        const media = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (cancelled) { media.getTracks().forEach(track => track.stop()); return; }
        stream.current = media;
        if (video.current) video.current.srcObject = media;
        setStage('ready');
      } catch {
        if (!cancelled) setStage('error');
      }
    };
    void acquire();
    return () => {
      cancelled = true;
      alive.current = false;
      if (capture.current) capture.current.cancel();
      else stream.current?.getTracks().forEach(track => track.stop());
      capture.current = null;
      stream.current = null;
    };
  }, [retry]);

  const start = () => {
    if (!stream.current || capture.current || stage !== 'ready') return;
    setRemaining(60);
    setStage('recording');
    capture.current = startCapture(stream.current,
      result => { if (alive.current) { stream.current = null; onRecordingComplete(result); } },
      () => { if (alive.current) { stream.current = null; setStage('error'); } },
      setRemaining);
  };
  const stop = () => {
    setStage('stopping');
    capture.current?.stop();
  };

  return (
    <div className="w-full flex flex-col items-center">
      <PracticeContextCard setup={setup} compact />
      <div className="relative w-full max-w-2xl aspect-video bg-gray-950 rounded-lg overflow-hidden shadow-2xl border border-gray-700">
        <video ref={video} autoPlay muted playsInline className="w-full h-full object-cover transform scale-x-[-1]" />
        {stage === 'recording' && <span className="absolute top-4 right-4 bg-black/50 px-3 py-1 rounded font-mono">{remaining}s</span>}
      </div>
      {stage === 'error' ? (
        <div role="alert" className="mt-6 text-center text-red-300">
          <p>Recording could not be completed. Check camera and microphone permissions and try again in a supported browser.</p>
          <button onClick={() => setRetry(value => value + 1)} className="mt-4 px-6 py-3 bg-gray-700 rounded-lg">Try Again</button>
        </div>
      ) : (
        <button onClick={stage === 'recording' ? stop : start}
          disabled={stage === 'loading' || stage === 'stopping'}
          className="mt-6 px-8 py-4 bg-red-600 text-white font-bold rounded-lg disabled:bg-gray-600">
          {stage === 'recording' ? 'Stop Recording' : stage === 'stopping' ? 'Finishing recording…' : stage === 'loading' ? 'Waiting for camera and microphone…' : 'Start Recording'}
        </button>
      )}
      <p className="mt-4 text-gray-400">{setup ? `Record for the selected ${setup.requested_duration_seconds}-second target.` : 'Explain a technical project to a non-technical person. Recording stops after 60 seconds.'}</p>
      <p className="mt-2 text-sm text-gray-400">Record at least 1 second. Video stays local for review; audio is sent for evaluation when you choose Get AI Feedback.</p>
    </div>
  );
};
export default RecordingScreen;
