/**
 * Urdu Translations (اردو ترجمہ)
 *
 * All UI text in Urdu for the Smart Todo ChatKit application.
 * Translated from English source.
 */

import type { TranslationKeys } from './en';

export const translations: TranslationKeys = {
  header: {
    title: 'سمارٹ ٹوڈو اسسٹنٹ',
    subtitle: 'اپنے کاموں کو منظم کرنے کے لیے قدرتی طور پر چیٹ کریں',
    newChatButton: '+ نئی چیٹ',
    newChatTooltip: 'نئی بات چیت شروع کریں',
  },

  welcome: {
    heading: 'خوش آمدید!',
    emoji: '👋',
    intro: 'میں آپ کا AI ٹوڈو اسسٹنٹ ہوں۔ کہنے کی کوشش کریں:',
    examples: [
      '"میرے کاموں میں گروسری خریدنا شامل کریں"',
      '"مجھے کل ماں کو فون کرنے کی یاد دلائیں"',
      '"میرے کام دکھائیں"',
      '"گروسری خریدنا مکمل کے طور پر نشان زد کریں"',
    ],
  },

  input: {
    placeholder: 'ایک پیغام ٹائپ کریں... (مثال کے طور پر، "دودھ خریدیں شامل کریں")',
    sendButton: 'بھیجیں',
    sendingButton: '⏳',
    disabledTooltip: 'بھیجنے کے لیے ایک پیغام درج کریں',
  },

  footer: {
    conversationLabel: 'گفتگو #',
    defaultMessage: 'نئی بات چیت شروع کریں',
  },

  messages: {
    userAvatar: '👤',
    assistantAvatar: '🤖',
    typingIndicator: 'ٹائپ کر رہے ہیں...',
  },

  errors: {
    prefix: '⚠️',
    close: '✕',
    invalidRequest: 'غلط درخواست۔ برائے مہربانی اپنے ان پٹ کو چیک کریں۔',
    permission: 'آپ کو اس گفتگو تک رسائی کی اجازت نہیں ہے۔',
    notFound: 'وسائل نہیں ملے۔',
    serviceUnavailable: 'سروس فی الوقت دستیاب نہیں ہے۔ برائے مہربانی ایک لمحے میں دوبارہ کوشش کریں۔',
    timeout: 'درخواست وقت ختم ہو گئی۔ برائے مہربانی دوبارہ کوشش کریں۔',
    generic: 'ایک خرابی واقع ہوئی۔ برائے مہربانی دوبارہ کوشش کریں۔',
    network: 'سرور تک پہنچنے میں ناکام۔ برائے مہربانی اپنا کنکشن چیک کریں۔',
    unexpected: 'ایک غیر متوقع خرابی واقع ہوئی۔',
    sendFailed: 'پیغام بھیجنے میں ناکام',
    requestSetupFailed: 'درخواست بھیجنے میں ناکام۔ برائے مہربانی دوبارہ کوشش کریں۔',
  },

  language: {
    en: 'EN',
    ur: 'UR',
    separator: '|',
  },
} as const;
