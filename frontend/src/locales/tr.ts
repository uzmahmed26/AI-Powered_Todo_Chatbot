/**
 * Turkish Translations (Türkçe)
 *
 * All UI text in Turkish for the Smart Todo ChatKit application.
 */

export const translations = {
  header: {
    title: 'Akıllı Yapılacaklar Asistanı',
    subtitle: 'Görevlerinizi yönetmek için doğal konuşun',
    newChatButton: '+ Yeni Sohbet',
    newChatTooltip: 'Yeni sohbet başlat',
  },

  welcome: {
    heading: 'Hoş Geldiniz!',
    emoji: '👋',
    intro: 'Ben sizin yapay zeka yapılacaklar asistanınızım. Deneyin:',
    examples: [
      '"Alışveriş yapmayı görevlerime ekle"',
      '"Yarın annemi aramayı hatırlat"',
      '"Görevlerimi göster"',
      '"Alışveriş yapmayı tamamlandı olarak işaretle"',
    ],
  },

  input: {
    placeholder: 'Bir mesaj yazın... (örn: \'Süt almayı ekle\')',
    sendButton: 'Gönder',
    sendingButton: '⏳',
    disabledTooltip: 'Göndermek için bir mesaj girin',
  },

  footer: {
    conversationLabel: 'Sohbet #',
    defaultMessage: 'Yeni bir sohbet başlatın',
  },

  messages: {
    userAvatar: '👤',
    assistantAvatar: '🤖',
    typingIndicator: 'Yazıyor...',
  },

  errors: {
    prefix: '⚠️',
    close: '✕',
    invalidRequest: 'Geçersiz istek. Lütfen girişinizi kontrol edin.',
    permission: 'Bu sohbete erişim izniniz yok.',
    notFound: 'Kaynak bulunamadı.',
    serviceUnavailable: 'Hizmet şu anda kullanılamıyor. Lütfen bir süre sonra tekrar deneyin.',
    timeout: 'İstek zaman aşımına uğradı. Lütfen tekrar deneyin.',
    generic: 'Bir hata oluştu. Lütfen tekrar deneyin.',
    network: 'Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.',
    unexpected: 'Beklenmeyen bir hata oluştu.',
    sendFailed: 'Mesaj gönderilemedi',
    requestSetupFailed: 'İstek gönderilemedi. Lütfen tekrar deneyin.',
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
      placeholder: 'Görevleri ara...',
    },
    filter: {
      status: 'Durum:',
      priority: 'Öncelik:',
      category: 'Kategori:',
      all: 'Tümü',
      pending: 'Beklemede',
      completed: 'Tamamlandı',
      high: 'Yüksek',
      medium: 'Orta',
      low: 'Düşük',
    },
    sort: {
      label: 'Sırala:',
      dueDate: 'Bitiş Tarihi',
      priority: 'Öncelik',
      title: 'Başlık',
    },
    empty: {
      icon: '📝',
      title: 'Görev bulunamadı',
      description: 'Arama veya filtreleri ayarlamayı deneyin',
    },
    card: {
      complete: 'Tamamla',
      delete: 'Sil',
      recurring: 'Tekrarlayan',
      due: 'Bitiş',
    },
    categories: {
      work: 'İş',
      home: 'Ev',
      study: 'Çalışma',
      shopping: 'Alışveriş',
      health: 'Sağlık',
      fitness: 'Fitness',
      personal: 'Kişisel',
    },
  },
};
