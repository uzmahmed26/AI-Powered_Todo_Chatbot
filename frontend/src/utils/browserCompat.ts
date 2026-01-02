/**
 * Browser Compatibility Utilities
 *
 * Checks for Web Speech API support and other browser features
 */

export interface BrowserCompatibility {
  webSpeechAPI: boolean;
  localStorage: boolean;
  userAgent: string;
  browserName: string;
}

/**
 * Check if Web Speech API is supported in the current browser
 *
 * @returns true if Web Speech API is available, false otherwise
 *
 * Browser Support:
 * - Chrome 90+: ✅ Full support
 * - Edge 90+: ✅ Full support
 * - Safari 14+: ✅ Supported (requires user permission)
 * - Firefox: ❌ Not supported
 */
export function isWebSpeechAPISupported(): boolean {
  return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
}

/**
 * Check if localStorage is available
 *
 * @returns true if localStorage is supported and accessible
 */
export function isLocalStorageSupported(): boolean {
  try {
    const testKey = '__localStorage_test__';
    localStorage.setItem(testKey, 'test');
    localStorage.removeItem(testKey);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Get browser name from user agent
 *
 * @returns Browser name (Chrome, Firefox, Safari, Edge, or Unknown)
 */
export function getBrowserName(): string {
  const userAgent = navigator.userAgent.toLowerCase();

  if (userAgent.indexOf('edg/') > -1) return 'Edge';
  if (userAgent.indexOf('chrome') > -1) return 'Chrome';
  if (userAgent.indexOf('safari') > -1) return 'Safari';
  if (userAgent.indexOf('firefox') > -1) return 'Firefox';

  return 'Unknown';
}

/**
 * Get comprehensive browser compatibility information
 *
 * @returns Object containing compatibility flags and browser info
 */
export function getBrowserCompatibility(): BrowserCompatibility {
  return {
    webSpeechAPI: isWebSpeechAPISupported(),
    localStorage: isLocalStorageSupported(),
    userAgent: navigator.userAgent,
    browserName: getBrowserName(),
  };
}

/**
 * Get SpeechRecognition constructor (handles vendor prefixes)
 *
 * @returns SpeechRecognition constructor or null if not supported
 */
export function getSpeechRecognition(): any | null {
  if ('SpeechRecognition' in window) {
    return (window as any).SpeechRecognition;
  }

  if ('webkitSpeechRecognition' in window) {
    return (window as any).webkitSpeechRecognition;
  }

  return null;
}
