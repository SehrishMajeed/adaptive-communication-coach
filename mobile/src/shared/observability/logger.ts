/**
 * Observability & Error Logging Boundary
 * 
 * This module acts as the boundary between the application and any external
 * crash reporting services (e.g. Sentry, Firebase Crashlytics).
 * 
 * It ensures that sensitive metadata (e.g., exact transcript texts, user audio URIs)
 * is redacted before it ever leaves the device or hits the system console.
 */

interface ErrorContext {
  [key: string]: unknown;
}

const REDACTED_STRING = '[REDACTED]';
const developmentConsole: Pick<Console, 'log' | 'error'> | undefined = globalThis.console;

/**
 * Strips PII and sensitive data from the error context.
 */
function redactContext(context: ErrorContext): ErrorContext {
  const redacted = { ...context };
  
  if (redacted.audioUri || redacted.videoUri) {
    redacted.audioUri = REDACTED_STRING;
    redacted.videoUri = REDACTED_STRING;
  }
  
  if (redacted.setup) {
    redacted.setup = { ...redacted.setup, transcript_redacted: true };
  }
  
  return redacted;
}

export const logger = {
  /**
   * Log standard application events (e.g., 'ScreenViewed', 'PracticeCompleted').
   */
  info: (message: string, context?: ErrorContext) => {
    const safeContext = context ? redactContext(context) : undefined;
    if (__DEV__) {
      developmentConsole?.log(`[INFO]: ${message}`, safeContext || '');
    }
    // Remote analytics can be wired here after consent, retention and redaction policy are finalized.
  },

  /**
   * Log handled errors, validation failures, or unhandled exceptions.
   */
  error: (error: Error | string, context?: ErrorContext) => {
    const errorMessage = error instanceof Error ? error.message : error;
    const safeContext = context ? redactContext(context) : undefined;
    
    if (__DEV__) {
      developmentConsole?.error(`[ERROR]: ${errorMessage}`, safeContext || '');
    }
    
    // Crash reporting can be wired here after consent, retention and redaction policy are finalized.
  }
};
