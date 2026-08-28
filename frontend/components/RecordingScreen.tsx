
import React, { useState, useRef, useEffect, useCallback } from 'react';

interface RecordingScreenProps {
  onRecordingComplete: (blob: Blob) => void;
}

const MAX_RECORDING_SECONDS = 60;

const RecordingScreen: React.FC<RecordingScreenProps> = ({ onRecordingComplete }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<number>(MAX_RECORDING_SECONDS);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  // FIX: Use ReturnType<typeof setInterval> for browser compatibility instead of NodeJS.Timeout
  const countdownIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const setupStream = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error("Error accessing media devices.", err);
      setError("Could not access camera and microphone. Please check your browser permissions.");
    }
  }, []);

  useEffect(() => {
    setupStream();
    return () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  const startRecording = () => {
    if (!stream) return;
    chunksRef.current = [];
    const recorder = new MediaRecorder(stream);
    mediaRecorderRef.current = recorder;
    
    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunksRef.current.push(event.data);
      }
    };
    
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      onRecordingComplete(blob);
    };
    
    recorder.start();
    setIsRecording(true);
    setCountdown(MAX_RECORDING_SECONDS);
    countdownIntervalRef.current = setInterval(() => {
        setCountdown(prev => {
            if (prev <= 1) {
                stopRecording();
                return 0;
            }
            return prev - 1;
        });
    }, 1000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if(countdownIntervalRef.current) {
          clearInterval(countdownIntervalRef.current);
      }
    }
  };

  if (error) {
    return <div className="text-center p-8 bg-red-900/50 rounded-lg"><p>{error}</p></div>;
  }

  return (
    <div className="w-full flex flex-col items-center">
      <div className="relative w-full max-w-2xl aspect-video bg-gray-950 rounded-lg overflow-hidden shadow-2xl border border-gray-700">
        <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover transform scale-x-[-1]"></video>
        {isRecording && (
          <div className="absolute top-4 right-4 flex items-center space-x-2 bg-black/50 px-3 py-1 rounded-full">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="font-mono text-sm">00:{countdown.toString().padStart(2, '0')}</span>
          </div>
        )}
      </div>
      <div className="mt-6">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={!stream}
            className="px-8 py-4 bg-red-600 text-white font-bold rounded-lg hover:bg-red-500 transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>
            <span>Start Recording</span>
          </button>
        ) : (
          <button
            onClick={stopRecording}
            className="px-8 py-4 bg-gray-600 text-white font-bold rounded-lg hover:bg-gray-500 transition-colors flex items-center space-x-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
            <span>Stop Recording</span>
          </button>
        )}
      </div>
      <p className="mt-4 text-gray-400">Recording will automatically stop after {MAX_RECORDING_SECONDS} seconds.</p>
    </div>
  );
};

export default RecordingScreen;
