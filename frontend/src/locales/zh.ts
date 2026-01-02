/**
 * Chinese Translations (简体中文)
 *
 * All UI text in Chinese for the Smart Todo ChatKit application.
 */

export const translations = {
  header: {
    title: '智能待办助手',
    subtitle: '自然对话管理您的任务',
    newChatButton: '+ 新对话',
    newChatTooltip: '开始新对话',
  },

  welcome: {
    heading: '欢迎！',
    emoji: '👋',
    intro: '我是您的AI待办助手。试试说：',
    examples: [
      '"添加购买杂货到我的任务"',
      '"提醒我明天给妈妈打电话"',
      '"显示我的任务"',
      '"标记购买杂货为已完成"',
    ],
  },

  input: {
    placeholder: '输入消息... (例如：\'添加购买牛奶\')',
    sendButton: '发送',
    sendingButton: '⏳',
    disabledTooltip: '输入消息以发送',
  },

  footer: {
    conversationLabel: '对话 #',
    defaultMessage: '开始新对话',
  },

  messages: {
    userAvatar: '👤',
    assistantAvatar: '🤖',
    typingIndicator: '正在输入...',
  },

  errors: {
    prefix: '⚠️',
    close: '✕',
    invalidRequest: '无效的请求。请检查您的输入。',
    permission: '您没有权限访问此对话。',
    notFound: '未找到资源。',
    serviceUnavailable: '服务当前不可用。请稍后再试。',
    timeout: '请求超时。请重试。',
    generic: '发生错误。请重试。',
    network: '无法连接到服务器。请检查您的连接。',
    unexpected: '发生意外错误。',
    sendFailed: '发送消息失败',
    requestSetupFailed: '发送请求失败。请重试。',
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
      title: '智能待办助手',
      subtitle: '与AI自然对话，轻松管理您的任务',
      description: '您的智能任务管理器由GPT-4驱动。只需告诉我您需要做什么，我将帮助您组织、优先处理和完成任务。',
      getStarted: '开始使用 - 免费',
      signIn: '登录',
      goToDashboard: '前往仪表板 →',
    },
    preview: {
      user1: '添加购买杂货到我的任务',
      assistant1: '已将"购买杂货"添加到您的任务！',
      user2: '显示我今天的任务',
      assistant2: '您有3个任务：购买杂货、给妈妈打电话、完成报告',
    },
    features: {
      title: '强大功能',
      subtitle: '您保持井然有序所需的一切',
      naturalLanguage: {
        title: '自然语言',
        description: '只需自然交谈 - 无需复杂命令或点击按钮',
      },
      multiLanguage: {
        title: '多语言',
        description: '支持英语、乌尔都语、阿拉伯语、中文和土耳其语',
      },
      voiceInput: {
        title: '语音输入',
        description: '说出您的任务 - 免提任务管理',
      },
      recurringTasks: {
        title: '重复任务',
        description: '设置每日、每周或每月重复任务',
      },
      smartSearch: {
        title: '智能搜索',
        description: '使用强大的搜索和过滤器即时查找任务',
      },
      aiPowered: {
        title: 'AI驱动',
        description: 'GPT-4理解上下文并帮助您保持井然有序',
      },
    },
    cta: {
      title: '准备好整理了吗？',
      subtitle: '加入数千名使用AI管理任务的用户',
      button: '立即免费开始 →',
    },
    footer: {
      text: '© 2026 智能待办助手。使用GPT-4和❤️构建',
    },
  },

  auth: {
    signin: {
      title: '登录您的账户',
      subtitle: '没有账户？',
      signupLink: '注册',
      emailPlaceholder: '电子邮件地址',
      passwordPlaceholder: '密码',
      submitButton: '登录',
      submittingButton: '登录中...',
      invalidCredentials: '电子邮件或密码无效',
    },
    signup: {
      title: '创建您的账户',
      subtitle: '已有账户？',
      signinLink: '登录',
      fullNamePlaceholder: '全名',
      emailPlaceholder: '电子邮件地址',
      passwordPlaceholder: '密码（至少8个字符）',
      confirmPasswordPlaceholder: '确认密码',
      submitButton: '注册',
      submittingButton: '创建账户中...',
      passwordMismatch: '密码不匹配',
      passwordTooShort: '密码必须至少8个字符',
      signupFailed: '注册失败',
    },
  },

  tasks: {
    search: {
      placeholder: '搜索任务...',
    },
    filter: {
      status: '状态:',
      priority: '优先级:',
      category: '类别:',
      all: '全部',
      pending: '待办',
      completed: '已完成',
      high: '高',
      medium: '中',
      low: '低',
    },
    sort: {
      label: '排序:',
      dueDate: '截止日期',
      priority: '优先级',
      title: '标题',
    },
    empty: {
      icon: '📝',
      title: '未找到任务',
      description: '尝试调整搜索或筛选条件',
    },
    card: {
      complete: '完成',
      delete: '删除',
      recurring: '重复',
      due: '截止',
    },
    categories: {
      work: '工作',
      home: '家庭',
      study: '学习',
      shopping: '购物',
      health: '健康',
      fitness: '健身',
      personal: '个人',
    },
  },
};
