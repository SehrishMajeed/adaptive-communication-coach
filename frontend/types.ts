
export enum AppState {
  WELCOME = 'WELCOME',
  RECORDING = 'RECORDING',
  REVIEW = 'REVIEW',
  ANALYZING = 'ANALYZING',
  FEEDBACK = 'FEEDBACK',
}

export enum ReviewMode {
  FULL = 'FULL',
  MUTED = 'MUTED',
  AUDIO_ONLY = 'AUDIO_ONLY',
}

export interface AIFeedback {
  overallImpression: string;
  confidenceScore: number;
  clarityScore: number;
  engagementScore: number;
  strengths: {
    bodyLanguage: string[];
    vocalVariety: string[];
    content: string[];
  };
  areasForImprovement: {
    bodyLanguage: string[];
    vocalVariety: string[];
    content: string[];
  };
  fillerWords: { word: string; count: number }[];
  pace: {
    wpm: number;
    feedback: string;
  };
  actionableTips: string[];
}
