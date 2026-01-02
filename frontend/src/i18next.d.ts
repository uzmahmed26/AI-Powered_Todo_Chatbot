/**
 * i18next Type Augmentation
 *
 * This file augments i18next types to provide proper TypeScript support
 * for our translation keys.
 */

import 'i18next';
import { translations } from './locales/en';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: {
      translation: typeof translations;
    };
  }
}
