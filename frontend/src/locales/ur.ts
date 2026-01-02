/**
 * Urdu Translations (اردو ترجمہ)
 *
 * All UI text in Urdu for the Smart Todo ChatKit application.
 * Translated from English source.
 */

import { translations as en } from './en';

export const translations: typeof en = {
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
    ar: 'AR',
    zh: 'ZH',
    tr: 'TR',
    separator: '|',
  },

  home: {
    hero: {
      title: 'سمارٹ ٹوڈو اسسٹنٹ',
      subtitle: 'AI کے ساتھ قدرتی طور پر چیٹ کر کے اپنے کاموں کو آسانی سے منظم کریں',
      description: 'GPT-4 کی طاقت سے چلنے والا آپ کا ذہین ٹاسک مینیجر۔ بس مجھے بتائیں کہ آپ کو کیا کرنا ہے، اور میں آپ کو منظم کرنے، ترجیح دینے اور اپنے کاموں کو مکمل کرنے میں مدد کروں گا۔',
      getStarted: 'شروع کریں - یہ مفت ہے',
      signIn: 'سائن ان کریں',
      goToDashboard: 'ڈیش بورڈ پر جائیں ←',
    },
    preview: {
      user1: 'میرے کاموں میں گروسری خریدنا شامل کریں',
      assistant1: 'آپ کے کاموں میں "گروسری خریدنا" شامل کر دیا گیا!',
      user2: 'آج کے میرے کام دکھائیں',
      assistant2: 'آپ کے 3 کام ہیں: گروسری خریدیں، ماں کو فون کریں، رپورٹ ختم کریں',
    },
    features: {
      title: 'طاقتور خصوصیات',
      subtitle: 'منظم رہنے کے لیے آپ کو جو کچھ چاہیے',
      naturalLanguage: {
        title: 'قدرتی زبان',
        description: 'بس قدرتی طور پر بات کریں - کوئی پیچیدہ کمانڈ یا بٹن کلک کرنے کی ضرورت نہیں',
      },
      multiLanguage: {
        title: 'کثیر زبانیں',
        description: 'انگریزی، اردو، عربی، چینی اور ترکی کی حمایت کرتا ہے',
      },
      voiceInput: {
        title: 'آواز ان پٹ',
        description: 'اپنے کام بولیں - ہینڈز فری ٹاسک مینجمنٹ',
      },
      recurringTasks: {
        title: 'بار بار آنے والے کام',
        description: 'روزانہ، ہفتہ وار، یا ماہانہ دہرائے جانے والے کام سیٹ کریں',
      },
      smartSearch: {
        title: 'سمارٹ تلاش',
        description: 'طاقتور تلاش اور فلٹرز کے ساتھ فوری طور پر کام تلاش کریں',
      },
      aiPowered: {
        title: 'AI سے چلنے والا',
        description: 'GPT-4 سیاق و سباق کو سمجھتا ہے اور آپ کو منظم رہنے میں مدد کرتا ہے',
      },
    },
    cta: {
      title: 'منظم ہونے کے لیے تیار ہیں؟',
      subtitle: 'AI کے ساتھ اپنے کاموں کا انتظام کرنے والے ہزاروں صارفین میں شامل ہوں',
      button: 'ابھی مفت شروع کریں ←',
    },
    footer: {
      text: '© 2026 سمارٹ ٹوڈو اسسٹنٹ۔ GPT-4 اور ❤️ کے ساتھ بنایا گیا',
    },
  },

  auth: {
    signin: {
      title: 'اپنے اکاؤنٹ میں سائن ان کریں',
      subtitle: 'کوئی اکاؤنٹ نہیں ہے؟',
      signupLink: 'سائن اپ کریں',
      emailPlaceholder: 'ای میل ایڈریس',
      passwordPlaceholder: 'پاس ورڈ',
      submitButton: 'سائن ان کریں',
      submittingButton: 'سائن ان ہو رہا ہے...',
      invalidCredentials: 'غلط ای میل یا پاس ورڈ',
    },
    signup: {
      title: 'اپنا اکاؤنٹ بنائیں',
      subtitle: 'پہلے سے اکاؤنٹ موجود ہے؟',
      signinLink: 'سائن ان کریں',
      fullNamePlaceholder: 'پورا نام',
      emailPlaceholder: 'ای میل ایڈریس',
      passwordPlaceholder: 'پاس ورڈ (کم از کم 8 حروف)',
      confirmPasswordPlaceholder: 'پاس ورڈ کی تصدیق کریں',
      submitButton: 'سائن اپ کریں',
      submittingButton: 'اکاؤنٹ بنایا جا رہا ہے...',
      passwordMismatch: 'پاس ورڈ مماثل نہیں ہیں',
      passwordTooShort: 'پاس ورڈ کم از کم 8 حروف کا ہونا چاہیے',
      signupFailed: 'سائن اپ ناکام ہو گیا',
    },
  },

  tasks: {
    search: {
      placeholder: 'کام تلاش کریں...',
    },
    filter: {
      status: 'حالت:',
      priority: 'ترجیح:',
      category: 'زمرہ:',
      all: 'تمام',
      pending: 'زیر التواء',
      completed: 'مکمل',
      high: 'اعلیٰ',
      medium: 'درمیانہ',
      low: 'کم',
    },
    sort: {
      label: 'ترتیب دیں:',
      dueDate: 'مقررہ تاریخ',
      priority: 'ترجیح',
      title: 'عنوان',
    },
    empty: {
      icon: '📝',
      title: 'کوئی کام نہیں ملا',
      description: 'اپنی تلاش یا فلٹرز کو ایڈجسٹ کرنے کی کوشش کریں',
    },
    card: {
      complete: 'مکمل کریں',
      delete: 'حذف کریں',
      recurring: 'بار بار آنے والا',
      due: 'مقررہ تاریخ',
    },
    categories: {
      work: 'کام',
      home: 'گھر',
      study: 'مطالعہ',
      shopping: 'خریداری',
      health: 'صحت',
      fitness: 'فٹنس',
      personal: 'ذاتی',
    },
  },
} as const;
