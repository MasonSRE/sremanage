/**
 * 定时器管理器 - 防止内存泄露的定时器管理工具
 * 
 * 使用方式:
 * 1. 在组件中创建实例：const timerManager = new TimerManager()
 * 2. 使用管理器创建定时器：timerManager.setInterval(callback, interval)
 * 3. 在组件卸载时清理：timerManager.clearAll()
 */

class TimerManager {
  constructor() {
    this.timers = new Set()
    this.timeouts = new Set()
    this.intervals = new Set()
  }

  /**
   * 设置一个被管理的定时器（setInterval）
   * @param {Function} callback - 回调函数
   * @param {number} delay - 延迟时间（毫秒）
   * @returns {number} - 定时器ID
   */
  setInterval(callback, delay) {
    const id = setInterval(callback, delay)
    this.intervals.add(id)
    this.timers.add({ type: 'interval', id })
    return id
  }

  /**
   * 设置一个被管理的超时定时器（setTimeout）
   * @param {Function} callback - 回调函数
   * @param {number} delay - 延迟时间（毫秒）
   * @returns {number} - 定时器ID
   */
  setTimeout(callback, delay) {
    const id = setTimeout(() => {
      // 自动从管理列表中移除已执行的timeout
      this.timeouts.delete(id)
      this.timers.delete({ type: 'timeout', id })
      callback()
    }, delay)
    this.timeouts.add(id)
    this.timers.add({ type: 'timeout', id })
    return id
  }

  /**
   * 清除指定的定时器
   * @param {number} id - 定时器ID
   */
  clearTimer(id) {
    if (this.intervals.has(id)) {
      clearInterval(id)
      this.intervals.delete(id)
    }
    if (this.timeouts.has(id)) {
      clearTimeout(id)
      this.timeouts.delete(id)
    }
    // 从总列表中移除
    this.timers.forEach(timer => {
      if (timer.id === id) {
        this.timers.delete(timer)
      }
    })
  }

  /**
   * 清除所有被管理的定时器
   */
  clearAll() {
    // 清除所有interval
    this.intervals.forEach(id => {
      clearInterval(id)
    })
    this.intervals.clear()

    // 清除所有timeout
    this.timeouts.forEach(id => {
      clearTimeout(id)
    })
    this.timeouts.clear()

    // 清空总列表
    this.timers.clear()

    console.log('TimerManager: 所有定时器已清理')
  }

  /**
   * 获取当前管理的定时器数量
   * @returns {object} - 定时器统计信息
   */
  getStats() {
    return {
      totalTimers: this.timers.size,
      intervals: this.intervals.size,
      timeouts: this.timeouts.size
    }
  }

  /**
   * 检查是否有正在运行的定时器
   * @returns {boolean}
   */
  hasActiveTimers() {
    return this.timers.size > 0
  }

  /**
   * 设置一个自动重试的定时器
   * @param {Function} callback - 回调函数，应该返回Promise
   * @param {number} interval - 重试间隔（毫秒）
   * @param {number} maxRetries - 最大重试次数，-1表示无限重试
   * @param {Function} onError - 错误处理函数
   * @returns {object} - 包含stop方法的控制对象
   */
  setRetryInterval(callback, interval, maxRetries = -1, onError = null) {
    let retryCount = 0
    let stopped = false
    
    const retry = async () => {
      if (stopped) return
      
      try {
        await callback()
        retryCount = 0 // 成功后重置重试计数
      } catch (error) {
        retryCount++
        
        if (onError) {
          onError(error, retryCount)
        }
        
        // 如果达到最大重试次数，停止重试
        if (maxRetries > 0 && retryCount >= maxRetries) {
          this.clearTimer(intervalId)
          console.warn(`TimerManager: 达到最大重试次数 ${maxRetries}，停止重试`)
          return
        }
      }
    }
    
    const intervalId = this.setInterval(retry, interval)
    
    return {
      stop: () => {
        stopped = true
        this.clearTimer(intervalId)
      },
      getRetryCount: () => retryCount
    }
  }
}

/**
 * Vue 3 组合式API的定时器管理Hook
 * @returns {object} - 定时器管理器实例和清理函数
 */
export function useTimerManager() {
  const timerManager = new TimerManager()

  // 在组件卸载时自动清理
  const { onBeforeUnmount } = require('vue')
  onBeforeUnmount(() => {
    timerManager.clearAll()
  })

  return {
    timerManager,
    clearAllTimers: () => timerManager.clearAll(),
    getTimerStats: () => timerManager.getStats()
  }
}

export default TimerManager