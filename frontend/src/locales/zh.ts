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
