/**
 * Speech Recognition Hook
 *
 * Custom hook for Web Speech API integration.
 * Supports English and Urdu speech recognition.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { Language } from '../types/translation';

// Web Speech API types
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onstart: (() => void) | null;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
}

// Browser compatibility check
const SpeechRecognitionAPI =
  (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

interface UseSpeechRecognitionOptions {
  language: Language;
  onResult?: (transcript: string) => void;
  onError?: (error: string) => void;
}

interface UseSpeechRecognitionReturn {
  isListening: boolean;
  transcript: string;
  isSupported: boolean;
  startListening: () => void;
  stopListening: () => void;
  resetTranscript: () => void;
}

/**
 * Custom hook for speech recognition
 */
export const useSpeechRecognition = (
  options: UseSpeechRecognitionOptions
): UseSpeechRecognitionReturn => {
  const { language, onResult, onError } = options;

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  // Check browser support
  const isSupported = Boolean(SpeechRecognitionAPI);

  // Language mapping for Web Speech API
  const getLanguageCode = (lang: Language): string => {
    return lang === 'ur' ? 'ur-PK' : 'en-US';
  };

  // Initialize speech recognition
  useEffect(() => {
    if (!isSupported) {
      console.warn('[SpeechRecognition] Web Speech API not supported');
      return;
    }

    console.log('[SpeechRecognition] Initializing for language:', language);

    const recognition = new SpeechRecognitionAPI() as SpeechRecognition;
    recognition.continuous = false;
    recognition.interimResults = true; // Enable interim results for better UX
    recognition.lang = getLanguageCode(language);

    console.log('[SpeechRecognition] Language code set to:', recognition.lang);

    // Handle start
    recognition.onstart = () => {
      console.log('[SpeechRecognition] Started listening');
      setIsListening(true);
    };

    // Handle results
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      console.log('[SpeechRecognition] Result received');
      const results = event.results;
      const lastResult = results[results.length - 1];
      const transcriptText = lastResult[0].transcript;
      const isFinal = lastResult.isFinal;

      console.log('[SpeechRecognition] Transcript:', transcriptText, 'isFinal:', isFinal);

      // Update transcript (both interim and final)
      setTranscript(transcriptText);

      // Only call onResult callback for final results
      if (isFinal && onResult) {
        onResult(transcriptText);
      }
    };

    // Handle errors
    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('[SpeechRecognition] Error:', event.error, event.message);
      setIsListening(false);

      // Don't show error for no-speech - it's normal if user doesn't speak
      if (event.error === 'no-speech') {
        console.log('[SpeechRecognition] No speech detected - user did not speak');
        return; // Silently ignore
      }

      const errorMessage =
        event.error === 'not-allowed'
          ? 'Microphone access denied. Please allow microphone permissions.'
          : event.error === 'aborted'
          ? 'Speech recognition was stopped.'
          : `Speech recognition error: ${event.error}. Please try again.`;

      if (onError) {
        onError(errorMessage);
      }
    };

    // Handle end
    recognition.onend = () => {
      console.log('[SpeechRecognition] Stopped listening');
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    console.log('[SpeechRecognition] Recognition object created and stored in ref');

    return () => {
      console.log('[SpeechRecognition] Cleanup - aborting recognition');
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, [isSupported, language]);

  // Start listening
  const startListening = useCallback(() => {
    console.log('[SpeechRecognition] startListening called');
    console.log('[SpeechRecognition] isSupported:', isSupported);
    console.log('[SpeechRecognition] isListening:', isListening);
    console.log('[SpeechRecognition] recognitionRef.current:', recognitionRef.current);

    if (!isSupported) {
      console.warn('[SpeechRecognition] Not supported, cannot start');
      if (onError) {
        onError('Speech recognition not supported in this browser.');
      }
      return;
    }

    if (!recognitionRef.current) {
      console.error('[SpeechRecognition] Recognition object not initialized');
      return;
    }

    if (isListening) {
      console.log('[SpeechRecognition] Already listening, skipping start');
      return;
    }

    try {
      // Update language before starting
      const langCode = getLanguageCode(language);
      console.log('[SpeechRecognition] Setting language to:', langCode);
      recognitionRef.current.lang = langCode;

      console.log('[SpeechRecognition] Calling recognition.start()...');
      recognitionRef.current.start();
      console.log('[SpeechRecognition] recognition.start() called successfully');

      setTranscript(''); // Clear previous transcript
    } catch (error) {
      console.error('[SpeechRecognition] Start error:', error);
      setIsListening(false);
      if (onError) {
        onError(`Failed to start: ${error}`);
      }
    }
  }, [isSupported, isListening, language, onError]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, [isListening]);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return {
    isListening,
    transcript,
    isSupported,
    startListening,
    stopListening,
    resetTranscript,
  };
};
