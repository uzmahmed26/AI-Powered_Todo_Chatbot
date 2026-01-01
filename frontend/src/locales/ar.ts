/**
 * Arabic Translations (العربية)
 *
 * All UI text in Arabic for the Smart Todo ChatKit application.
 */

export const translations = {
  header: {
    title: 'مساعد المهام الذكي',
    subtitle: 'تحدث بشكل طبيعي لإدارة مهامك',
    newChatButton: '+ محادثة جديدة',
    newChatTooltip: 'بدء محادثة جديدة',
  },

  welcome: {
    heading: 'مرحباً!',
    emoji: '👋',
    intro: 'أنا مساعدك الذكي للمهام. جرب قول:',
    examples: [
      '"أضف شراء البقالة إلى مهامي"',
      '"ذكرني بالاتصال بأمي غداً"',
      '"اعرض مهامي"',
      '"ضع علامة على شراء البقالة كمنجز"',
    ],
  },

  input: {
    placeholder: 'اكتب رسالة... (مثال: "أضف شراء الحليب")',
    sendButton: 'إرسال',
    sendingButton: '⏳',
    disabledTooltip: 'أدخل رسالة للإرسال',
  },

  footer: {
    conversationLabel: 'محادثة #',
    defaultMessage: 'ابدأ محادثة جديدة',
  },

  messages: {
    userAvatar: '👤',
    assistantAvatar: '🤖',
    typingIndicator: 'جاري الكتابة...',
  },

  errors: {
    prefix: '⚠️',
    close: '✕',
    invalidRequest: 'طلب غير صالح. يرجى التحقق من المدخلات.',
    permission: 'ليس لديك إذن للوصول إلى هذه المحادثة.',
    notFound: 'المورد غير موجود.',
    serviceUnavailable: 'الخدمة غير متاحة حالياً. يرجى المحاولة مرة أخرى لاحقاً.',
    timeout: 'انتهت مهلة الطلب. يرجى المحاولة مرة أخرى.',
    generic: 'حدث خطأ. يرجى المحاولة مرة أخرى.',
    network: 'غير قادر على الوصول إلى الخادم. يرجى التحقق من الاتصال.',
    unexpected: 'حدث خطأ غير متوقع.',
    sendFailed: 'فشل إرسال الرسالة',
    requestSetupFailed: 'فشل إرسال الطلب. يرجى المحاولة مرة أخرى.',
  },

  language: {
    en: 'EN',
    ur: 'UR',
    ar: 'AR',
    zh: 'ZH',
    tr: 'TR',
    separator: '|',
  },

  tasks: {
    search: {
      placeholder: 'البحث عن المهام...',
    },
    filter: {
      status: 'الحالة:',
      priority: 'الأولوية:',
      category: 'الفئة:',
      all: 'الكل',
      pending: 'قيد الانتظار',
      completed: 'مكتمل',
      high: 'عالية',
      medium: 'متوسطة',
      low: 'منخفضة',
    },
    sort: {
      label: 'ترتيب حسب:',
      dueDate: 'تاريخ الاستحقاق',
      priority: 'الأولوية',
      title: 'العنوان',
    },
    empty: {
      icon: '📝',
      title: 'لا توجد مهام',
      description: 'حاول تعديل البحث أو الفلاتر',
    },
    card: {
      complete: 'إكمال',
      delete: 'حذف',
      recurring: 'متكررة',
      due: 'الاستحقاق',
    },
    categories: {
      work: 'عمل',
      home: 'منزل',
      study: 'دراسة',
      shopping: 'تسوق',
      health: 'صحة',
      fitness: 'لياقة',
      personal: 'شخصي',
    },
  },
};
