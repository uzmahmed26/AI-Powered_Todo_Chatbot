/**
 * Voice Input Button Component
 *
 * Microphone button for speech-to-text input.
 * Supports English and Urdu speech recognition.
 */

import React, { useEffect } from 'react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useLanguage } from '../contexts/LanguageContext';
import './VoiceInputButton.css';

interface VoiceInputButtonProps {
  onTranscript: (text: string) => void;
  onListeningChange?: (isListening: boolean) => void;
  disabled?: boolean;
}

const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  onTranscript,
  onListeningChange,
  disabled = false,
}) => {
  const { language } = useLanguage();

  const { isListening, isSupported, startListening, stopListening } = useSpeechRecognition({
    language,
    onResult: (transcript) => {
      console.log('[VoiceInputButton] Received transcript:', transcript);
      onTranscript(transcript);
    },
    onError: (error) => {
      console.error('[VoiceInputButton] Error:', error);
    },
  });

  // Notify parent when listening state changes
  useEffect(() => {
    if (onListeningChange) {
      onListeningChange(isListening);
    }
  }, [isListening, onListeningChange]);

  // Debug logging on mount and updates
  useEffect(() => {
    console.log('[VoiceInputButton] Component rendered');
    console.log('[VoiceInputButton] isSupported:', isSupported);
    console.log('[VoiceInputButton] language:', language);
    console.log('[VoiceInputButton] disabled:', disabled);
  }, [isSupported, language, disabled]);

  // Don't render if not supported
  if (!isSupported) {
    console.warn('[VoiceInputButton] Web Speech API not supported - button will not render');
    return null;
  }

  const handleClick = () => {
    console.log('[VoiceInputButton] Click handler called');
    console.log('[VoiceInputButton] isListening:', isListening);

    if (isListening) {
      console.log('[VoiceInputButton] Stopping listening');
      stopListening();
    } else {
      console.log('[VoiceInputButton] Starting listening');
      startListening();
    }
  };

  return (
    <button
      type="button"
      className={`voice-input-button ${isListening ? 'listening' : ''}`}
      onClick={handleClick}
      disabled={disabled}
      title={isListening ? 'Stop recording' : 'Start voice input'}
      aria-label={isListening ? 'Stop recording' : 'Start voice input'}
    >
      {isListening ? '⏹️' : '🎤'}
    </button>
  );
};

export default VoiceInputButton;
