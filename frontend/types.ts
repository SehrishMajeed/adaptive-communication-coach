export enum AppState {
  WELCOME = 'WELCOME', RECORDING = 'RECORDING', REVIEW = 'REVIEW',
  ANALYZING = 'ANALYZING', FEEDBACK = 'FEEDBACK',
}
export enum ReviewMode { FULL = 'FULL', MUTED = 'MUTED', AUDIO_ONLY = 'AUDIO_ONLY' }

export * from '../shared/types';
