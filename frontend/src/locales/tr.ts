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

  home: {
    hero: {
      title: 'Akıllı Yapılacaklar Asistanı',
      subtitle: 'Görevlerinizi zahmetsizce yönetmek için AI ile doğal konuşun',
      description: 'GPT-4 ile desteklenen akıllı görev yöneticiniz. Sadece ne yapmanız gerektiğini söyleyin, size organize olmanızda, önceliklendirmenizde ve görevlerinizi tamamlamanızda yardımcı olacağım.',
      getStarted: 'Başlayın - Ücretsiz',
      signIn: 'Giriş Yap',
      goToDashboard: 'Panoya Git →',
    },
    preview: {
      user1: 'Alışveriş yapmayı görevlerime ekle',
      assistant1: 'Görevlerinize "alışveriş yapmak" eklendi!',
      user2: 'Bugünkü görevlerimi göster',
      assistant2: '3 göreviniz var: alışveriş yap, annemi ara, raporu bitir',
    },
    features: {
      title: 'Güçlü Özellikler',
      subtitle: 'Organize kalmak için ihtiyacınız olan her şey',
      naturalLanguage: {
        title: 'Doğal Dil',
        description: 'Sadece doğal konuşun - karmaşık komutlar veya tıklanacak düğmeler yok',
      },
      multiLanguage: {
        title: 'Çok Dilli',
        description: 'İngilizce, Urduca, Arapça, Çince ve Türkçe destekler',
      },
      voiceInput: {
        title: 'Sesli Giriş',
        description: 'Görevlerinizi söyleyin - eller serbest görev yönetimi',
      },
      recurringTasks: {
        title: 'Yinelenen Görevler',
        description: 'Günlük, haftalık veya aylık tekrarlayan görevler ayarlayın',
      },
      smartSearch: {
        title: 'Akıllı Arama',
        description: 'Güçlü arama ve filtrelerle görevleri anında bulun',
      },
      aiPowered: {
        title: 'AI Destekli',
        description: 'GPT-4 bağlamı anlar ve organize kalmanıza yardımcı olur',
      },
    },
    cta: {
      title: 'Organize olmaya hazır mısınız?',
      subtitle: 'Görevlerini AI ile yöneten binlerce kullanıcıya katılın',
      button: 'Şimdi Ücretsiz Başlayın →',
    },
    footer: {
      text: '© 2026 Akıllı Yapılacaklar Asistanı. GPT-4 ve ❤️ ile yapıldı',
    },
  },

  auth: {
    signin: {
      title: 'Hesabınıza giriş yapın',
      subtitle: 'Hesabınız yok mu?',
      signupLink: 'Kayıt olun',
      emailPlaceholder: 'E-posta adresi',
      passwordPlaceholder: 'Şifre',
      submitButton: 'Giriş yap',
      submittingButton: 'Giriş yapılıyor...',
      invalidCredentials: 'Geçersiz e-posta veya şifre',
    },
    signup: {
      title: 'Hesabınızı oluşturun',
      subtitle: 'Zaten hesabınız var mı?',
      signinLink: 'Giriş yap',
      fullNamePlaceholder: 'Ad soyad',
      emailPlaceholder: 'E-posta adresi',
      passwordPlaceholder: 'Şifre (en az 8 karakter)',
      confirmPasswordPlaceholder: 'Şifreyi onayla',
      submitButton: 'Kayıt ol',
      submittingButton: 'Hesap oluşturuluyor...',
      passwordMismatch: 'Şifreler eşleşmiyor',
      passwordTooShort: 'Şifre en az 8 karakter olmalıdır',
      signupFailed: 'Kayıt başarısız oldu',
    },
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
