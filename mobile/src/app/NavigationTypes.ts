import type { PracticeSetup, PracticeAttemptResult } from '../../../shared/types';

export type RootStackParamList = {
  Setup: undefined;
  Record: { setup: PracticeSetup; sessionId?: number | null };
  Review: { 
    setup: PracticeSetup; 
    sessionId?: number | null;
    videoUri: string; 
    audioUri: string; 
    durationSeconds: number 
  };
  Feedback: { 
    setup: PracticeSetup; 
    result: PracticeAttemptResult 
  };
};
