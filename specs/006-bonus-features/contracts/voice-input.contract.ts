/**
 * Voice Input Contract
 *
 * Web Speech API integration for hands-free todo management.
 * Browser-native implementation, no backend API required.
 */

import { Language } from './language-detection.contract';

export interface VoiceInputSession {
  sessionId: string; // UUID
  isRecording: boolean;
  interimTranscript: string;
  finalTranscript: string;
  detectedLanguage: Language;
  confidenceScore?: number; // 0.0 - 1.0
  startedAt: Date;
  error?: VoiceInputError;
}

export interface VoiceInputError {
  code: 'permission-denied' | 'not-supported' | 'no-speech' | 'network' | 'timeout' | 'aborted';
  message: string;
  userMessage: string; // Localized, user-friendly message
}

export interface VoiceRecognitionConfig {
  language: Language;
  continuous: boolean; // Continue recognition after pause
  interimResults: boolean; // Emit partial results during speech
  maxAlternatives: number; // Number of alternative transcriptions
  maxDuration?: number; // Max recording duration in seconds (default: 30)
}

/**
 * Starts voice input session.
 *
 * @param config - Recognition configuration
 * @returns Session object
 * @throws VoiceInputError if browser doesn't support Web Speech API
 *
 * @sideEffects
 * - Requests microphone permission if not granted
 * - Initializes Web Speech API SpeechRecognition
 * - Starts audio capture
 *
 * @example
 * const session = await startVoiceInput({
 *   language: 'en',
 *   continuous: false,
 *   interimResults: true,
 *   maxAlternatives: 1,
 *   maxDuration: 30
 * });
 */
export function startVoiceInput(config: VoiceRecognitionConfig): Promise<VoiceInputSession>;

/**
 * Stops voice input session.
 *
 * @param sessionId - Session identifier
 * @returns Final session state with complete transcript
 *
 * @sideEffects
 * - Stops audio capture
 * - Finalizes transcription
 * - Releases microphone
 */
export function stopVoiceInput(sessionId: string): Promise<VoiceInputSession>;

/**
 * Cancels voice input session without saving transcript.
 *
 * @param sessionId - Session identifier
 *
 * @sideEffects
 * - Aborts recognition
 * - Discards transcript
 * - Releases microphone
 */
export function cancelVoiceInput(sessionId: string): void;

/**
 * Checks if Web Speech API is supported in current browser.
 *
 * @returns true if supported, false otherwise
 *
 * @browserSupport
 * - Chrome 90+: ✅ Full support
 * - Edge 90+: ✅ Full support
 * - Safari 14+: ✅ Supported (requires user permission)
 * - Firefox: ❌ Not supported
 */
export function isVoiceInputSupported(): boolean;

/**
 * Gets current microphone permission status.
 *
 * @returns Permission state
 */
export function getMicrophonePermissionStatus(): Promise<'granted' | 'denied' | 'prompt'>;

/**
 * Event emitted during voice recognition.
 */
export interface VoiceInputEvent {
  type: 'start' | 'interim' | 'final' | 'error' | 'end';
  sessionId: string;
  transcript?: string;
  confidence?: number;
  error?: VoiceInputError;
}

/**
 * Subscribe to voice input events.
 *
 * @param sessionId - Session identifier
 * @param callback - Event handler
 * @returns Unsubscribe function
 *
 * @example
 * const unsubscribe = subscribeToVoiceInput(sessionId, (event) => {
 *   if (event.type === 'interim') {
 *     console.log('Interim:', event.transcript);
 *   } else if (event.type === 'final') {
 *     console.log('Final:', event.transcript);
 *   } else if (event.type === 'error') {
 *     console.error('Error:', event.error);
 *   }
 * });
 *
 * // Later: unsubscribe()
 */
export function subscribeToVoiceInput(
  sessionId: string,
  callback: (event: VoiceInputEvent) => void
): () => void;
