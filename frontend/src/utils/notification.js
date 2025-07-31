/**
 * 通知工具类 - 提供友好的用户通知体验
 * 替换原生的alert, confirm等，提供更好的用户体验
 */

class NotificationManager {
  constructor() {
    this.notifications = []
    this.container = null
    this.zIndex = 9999
    this.init()
  }

  init() {
    // 创建通知容器
    this.container = document.createElement('div')
    this.container.id = 'notification-container'
    this.container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: ${this.zIndex};
      pointer-events: none;
      width: 400px;
      max-width: 90vw;
    `
    document.body.appendChild(this.container)
  }

  /**
   * 显示通知
   * @param {string} message - 通知消息
   * @param {string} type - 通知类型：success, error, warning, info
   * @param {number} duration - 持续时间（毫秒），0表示不自动消失
   * @param {object} options - 额外选项
   */
  show(message, type = 'info', duration = 5000, options = {}) {
    const notification = this.createNotification(message, type, duration, options)
    this.container.appendChild(notification.element)
    this.notifications.push(notification)

    // 触发动画
    setTimeout(() => {
      notification.element.classList.add('notification-show')
    }, 10)

    // 自动消失
    if (duration > 0) {
      setTimeout(() => {
        this.remove(notification.id)
      }, duration)
    }

    return notification.id
  }

  /**
   * 创建通知元素
   */
  createNotification(message, type, duration, options) {
    const id = Date.now() + Math.random()
    const element = document.createElement('div')
    
    const colors = {
      success: { bg: '#10B981', border: '#059669', icon: '✅' },
      error: { bg: '#EF4444', border: '#DC2626', icon: '❌' },
      warning: { bg: '#F59E0B', border: '#D97706', icon: '⚠️' },
      info: { bg: '#3B82F6', border: '#2563EB', icon: 'ℹ️' }
    }

    const color = colors[type] || colors.info
    
    element.style.cssText = `
      background: white;
      border-left: 4px solid ${color.border};
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
      margin-bottom: 10px;
      padding: 16px;
      pointer-events: auto;
      transform: translateX(100%);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      opacity: 0;
      max-width: 100%;
      word-wrap: break-word;
    `

    element.classList.add('notification')
    element.innerHTML = `
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <div style="font-size: 18px; flex-shrink: 0; margin-top: 2px;">
          ${color.icon}
        </div>
        <div style="flex: 1; min-width: 0;">
          <div style="color: #1F2937; font-weight: 600; margin-bottom: 4px; font-size: 14px;">
            ${this.getTypeTitle(type)}
          </div>
          <div style="color: #4B5563; font-size: 14px; line-height: 1.5;">
            ${message}
          </div>
          ${options.actions ? this.createActions(options.actions, id) : ''}
        </div>
        <button onclick="notificationManager.remove('${id}')" 
                style="background: none; border: none; color: #9CA3AF; cursor: pointer; font-size: 18px; padding: 0; margin-left: 8px; flex-shrink: 0;">
          ×
        </button>
      </div>
    `

    // 添加显示样式类
    const style = document.createElement('style')
    if (!document.getElementById('notification-styles')) {
      style.id = 'notification-styles'
      style.textContent = `
        .notification-show {
          transform: translateX(0) !important;
          opacity: 1 !important;
        }
        .notification-hide {
          transform: translateX(100%) !important;
          opacity: 0 !important;
        }
        .notification button:hover {
          color: #374151 !important;
        }
        .notification-action {
          margin-top: 8px;
          display: flex;
          gap: 8px;
        }
        .notification-action button {
          padding: 6px 12px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .notification-action .btn-primary {
          background: #3B82F6;
          color: white;
          border: none;
        }
        .notification-action .btn-primary:hover {
          background: #2563EB;
        }
        .notification-action .btn-secondary {
          background: #F3F4F6;
          color: #374151;
          border: 1px solid #D1D5DB;
        }
        .notification-action .btn-secondary:hover {
          background: #E5E7EB;
        }
      `
      document.head.appendChild(style)
    }

    return { id, element, type, message }
  }

  /**
   * 创建操作按钮
   */
  createActions(actions, notificationId) {
    const actionsHtml = actions.map(action => `
      <button class="btn-${action.type || 'secondary'}" 
              onclick="${action.handler}; notificationManager.remove('${notificationId}')">
        ${action.text}
      </button>
    `).join('')
    
    return `<div class="notification-action">${actionsHtml}</div>`
  }

  /**
   * 获取类型标题
   */
  getTypeTitle(type) {
    const titles = {
      success: '操作成功',
      error: '操作失败',
      warning: '警告提示',
      info: '信息提示'
    }
    return titles[type] || titles.info
  }

  /**
   * 移除通知
   */
  remove(id) {
    const notification = this.notifications.find(n => n.id === id)
    if (!notification) return

    notification.element.classList.add('notification-hide')
    
    setTimeout(() => {
      if (notification.element.parentNode) {
        notification.element.parentNode.removeChild(notification.element)
      }
      this.notifications = this.notifications.filter(n => n.id !== id)
    }, 300)
  }

  /**
   * 清除所有通知
   */
  clear() {
    this.notifications.forEach(notification => {
      this.remove(notification.id)
    })
  }

  /**
   * 成功通知
   */
  success(message, duration = 4000, options = {}) {
    return this.show(message, 'success', duration, options)
  }

  /**
   * 错误通知
   */
  error(message, duration = 6000, options = {}) {
    return this.show(message, 'error', duration, options)
  }

  /**
   * 警告通知
   */
  warning(message, duration = 5000, options = {}) {
    return this.show(message, 'warning', duration, options)
  }

  /**
   * 信息通知
   */
  info(message, duration = 4000, options = {}) {
    return this.show(message, 'info', duration, options)
  }

  /**
   * 确认对话框
   */
  confirm(message, title = '确认操作') {
    return new Promise((resolve) => {
      const actions = [
        {
          text: '取消',
          type: 'secondary',
          handler: `window.confirmCallback_${Date.now()}(false)`
        },
        {
          text: '确认',
          type: 'primary',
          handler: `window.confirmCallback_${Date.now()}(true)`
        }
      ]

      // 创建全局回调
      const callbackName = `confirmCallback_${Date.now()}`
      window[callbackName] = (result) => {
        delete window[callbackName]
        resolve(result)
      }

      this.show(`${title}: ${message}`, 'warning', 0, { actions })
    })
  }

  /**
   * 加载通知
   */
  loading(message = '处理中...') {
    const id = this.show(message, 'info', 0, {})
    const notification = this.notifications.find(n => n.id === id)
    
    if (notification) {
      // 添加加载动画
      const icon = notification.element.querySelector('div[style*="font-size: 18px"]')
      if (icon) {
        icon.innerHTML = '<div style="width: 18px; height: 18px; border: 2px solid #3B82F6; border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>'
        
        // 添加旋转动画
        if (!document.getElementById('loading-animation')) {
          const style = document.createElement('style')
          style.id = 'loading-animation'
          style.textContent = `
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `
          document.head.appendChild(style)
        }
      }
    }

    return {
      close: () => this.remove(id),
      update: (newMessage) => {
        if (notification) {
          const messageEl = notification.element.querySelector('div[style*="color: #4B5563"]')
          if (messageEl) messageEl.textContent = newMessage
        }
      }
    }
  }
}

// 创建全局实例
const notificationManager = new NotificationManager()

// 导出便捷方法
export const notify = {
  success: (message, duration, options) => notificationManager.success(message, duration, options),
  error: (message, duration, options) => notificationManager.error(message, duration, options),
  warning: (message, duration, options) => notificationManager.warning(message, duration, options),
  info: (message, duration, options) => notificationManager.info(message, duration, options),
  confirm: (message, title) => notificationManager.confirm(message, title),
  loading: (message) => notificationManager.loading(message),
  clear: () => notificationManager.clear()
}

// 替换原生alert的便捷方法
export const alert = (message) => notificationManager.info(message)
export const confirm = (message) => notificationManager.confirm(message)

// 导出管理器实例
export default notificationManager

// 挂载到全局对象，方便在HTML中直接调用
if (typeof window !== 'undefined') {
  window.notificationManager = notificationManager
  window.notify = notify
}