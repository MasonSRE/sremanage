/**
 * Loading状态管理器
 * 提供全局和局部的loading状态管理功能
 */

import { ref, reactive } from 'vue'
import { notify } from './notification'

class LoadingManager {
  constructor() {
    this.globalLoading = ref(false)
    this.loadingStates = reactive(new Map())
    this.loadingQueue = reactive(new Set())
    this.pendingOperations = reactive(new Map())
  }

  /**
   * 设置全局loading状态
   * @param {boolean} loading - loading状态
   * @param {string} message - loading消息
   */
  setGlobalLoading(loading, message = '') {
    this.globalLoading.value = loading
    if (loading && message) {
      this.showLoadingNotification(message)
    }
  }

  /**
   * 设置特定区域的loading状态
   * @param {string} key - loading状态的key
   * @param {boolean} loading - loading状态
   * @param {string} message - loading消息
   */
  setLoading(key, loading, message = '') {
    if (loading) {
      this.loadingStates.set(key, {
        loading: true,
        message,
        startTime: Date.now()
      })
      this.loadingQueue.add(key)
    } else {
      this.loadingStates.delete(key)
      this.loadingQueue.delete(key)
    }
  }

  /**
   * 检查特定key是否在loading
   * @param {string} key - loading状态的key
   * @returns {boolean}
   */
  isLoading(key) {
    return this.loadingStates.has(key)
  }

  /**
   * 获取loading状态信息
   * @param {string} key - loading状态的key
   * @returns {object|null}
   */
  getLoadingState(key) {
    return this.loadingStates.get(key) || null
  }

  /**
   * 检查是否有任何loading状态
   * @returns {boolean}
   */
  hasAnyLoading() {
    return this.globalLoading.value || this.loadingQueue.size > 0
  }

  /**
   * 获取所有loading状态
   * @returns {Map}
   */
  getAllLoadingStates() {
    return new Map(this.loadingStates)
  }

  /**
   * 清除所有loading状态
   */
  clearAll() {
    this.globalLoading.value = false
    this.loadingStates.clear()
    this.loadingQueue.clear()
    this.pendingOperations.clear()
  }

  /**
   * 包装异步操作，自动管理loading状态
   * @param {string} key - loading状态的key
   * @param {Function} operation - 异步操作函数
   * @param {object} options - 选项
   * @returns {Promise}
   */
  async withLoading(key, operation, options = {}) {
    const {
      message = '处理中...',
      errorMessage = '操作失败',
      successMessage = null,
      timeout = 30000,
      showNotification = true
    } = options

    // 设置loading状态
    this.setLoading(key, true, message)

    // 设置超时处理
    const timeoutId = setTimeout(() => {
      if (this.isLoading(key)) {
        this.setLoading(key, false)
        if (showNotification) {
          notify.error('操作超时，请重试')
        }
      }
    }, timeout)

    try {
      const result = await operation()

      // 成功处理
      if (successMessage && showNotification) {
        notify.success(successMessage)
      }

      return result

    } catch (error) {
      console.error(`操作失败 [${key}]:`, error)
      
      if (showNotification) {
        const message = error.message || errorMessage
        notify.error(message)
      }
      
      throw error

    } finally {
      // 清理
      clearTimeout(timeoutId)
      this.setLoading(key, false)
    }
  }

  /**
   * 批量操作管理器
   * @param {string} key - loading状态的key
   * @param {Array} operations - 操作数组
   * @param {object} options - 选项
   * @returns {Promise}
   */
  async withBatchLoading(key, operations, options = {}) {
    const {
      message = '批量处理中...',
      concurrent = 5,
      showProgress = true,
      showNotification = true
    } = options

    this.setLoading(key, true, message)

    const results = []
    const errors = []
    let completed = 0

    try {
      // 分批处理
      for (let i = 0; i < operations.length; i += concurrent) {
        const batch = operations.slice(i, i + concurrent)
        
        const batchResults = await Promise.allSettled(
          batch.map(async (operation, index) => {
            try {
              const result = await operation()
              completed++
              
              // 更新进度
              if (showProgress) {
                const progress = Math.round((completed / operations.length) * 100)
                this.setLoading(key, true, `${message} (${progress}%)`)
              }
              
              return { success: true, data: result, index: i + index }
            } catch (error) {
              completed++
              errors.push({ error, index: i + index })
              return { success: false, error, index: i + index }
            }
          })
        )

        results.push(...batchResults)
      }

      // 处理结果
      const successCount = results.filter(r => r.value?.success).length
      const errorCount = errors.length

      if (showNotification) {
        if (errorCount === 0) {
          notify.success(`批量操作完成，共处理 ${successCount} 项`)
        } else if (successCount > 0) {
          notify.warning(`批量操作部分完成，成功 ${successCount} 项，失败 ${errorCount} 项`)
        } else {
          notify.error(`批量操作失败，共 ${errorCount} 项失败`)
        }
      }

      return {
        results,
        errors,
        successCount,
        errorCount,
        total: operations.length
      }

    } finally {
      this.setLoading(key, false)
    }
  }

  /**
   * 显示loading通知
   * @param {string} message - 消息
   * @returns {object} - 通知控制器
   */
  showLoadingNotification(message) {
    return notify.loading(message)
  }

  /**
   * 防抖操作包装
   * @param {string} key - 操作key
   * @param {Function} operation - 操作函数
   * @param {number} delay - 防抖延迟
   * @returns {Function}
   */
  debounce(key, operation, delay = 300) {
    return (...args) => {
      // 清除之前的操作
      if (this.pendingOperations.has(key)) {
        clearTimeout(this.pendingOperations.get(key))
      }

      // 设置新的延时操作
      const timeoutId = setTimeout(async () => {
        try {
          await operation(...args)
        } finally {
          this.pendingOperations.delete(key)
        }
      }, delay)

      this.pendingOperations.set(key, timeoutId)
    }
  }

  /**
   * 节流操作包装
   * @param {string} key - 操作key
   * @param {Function} operation - 操作函数
   * @param {number} interval - 节流间隔
   * @returns {Function}
   */
  throttle(key, operation, interval = 1000) {
    let lastExecution = 0

    return async (...args) => {
      const now = Date.now()
      
      if (now - lastExecution >= interval) {
        lastExecution = now
        try {
          return await operation(...args)
        } catch (error) {
          console.error(`节流操作失败 [${key}]:`, error)
          throw error
        }
      }
    }
  }
}

// 全局loading管理器实例
const loadingManager = new LoadingManager()

/**
 * Vue 3 Composition API Hook
 * @param {string} namespace - 命名空间
 * @returns {object}
 */
export function useLoading(namespace = 'default') {
  const scopedKey = (key) => `${namespace}:${key}`

  return {
    // 状态
    globalLoading: loadingManager.globalLoading,
    
    // 方法
    setLoading: (key, loading, message) => 
      loadingManager.setLoading(scopedKey(key), loading, message),
    
    isLoading: (key) => 
      loadingManager.isLoading(scopedKey(key)),
    
    getLoadingState: (key) => 
      loadingManager.getLoadingState(scopedKey(key)),
    
    withLoading: (key, operation, options) => 
      loadingManager.withLoading(scopedKey(key), operation, options),
    
    withBatchLoading: (key, operations, options) => 
      loadingManager.withBatchLoading(scopedKey(key), operations, options),
    
    debounce: (key, operation, delay) => 
      loadingManager.debounce(scopedKey(key), operation, delay),
    
    throttle: (key, operation, interval) => 
      loadingManager.throttle(scopedKey(key), operation, interval),
    
    hasAnyLoading: () => loadingManager.hasAnyLoading(),
    clearAll: () => loadingManager.clearAll()
  }
}

export default loadingManager