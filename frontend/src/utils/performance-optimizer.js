/**
 * 前端性能优化工具模块
 * 提供防抖节流、预加载、性能监控等功能
 */

import { nextTick, ref, computed, watch } from 'vue'

// 防抖函数
export function debounce(func, wait, immediate = false) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      timeout = null
      if (!immediate) func.apply(this, args)
    }
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    if (callNow) func.apply(this, args)
  }
}

// 节流函数
export function throttle(func, limit) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

// 性能监控类
export class PerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.observers = new Map()
    this.isSupported = 'performance' in window
  }

  // 开始性能监控
  startMeasure(name) {
    if (!this.isSupported) return

    performance.mark(`${name}-start`)
    return name
  }

  // 结束性能监控
  endMeasure(name) {
    if (!this.isSupported) return 0

    performance.mark(`${name}-end`)
    performance.measure(name, `${name}-start`, `${name}-end`)
    
    const measure = performance.getEntriesByName(name)[0]
    const duration = measure ? measure.duration : 0
    
    // 记录指标
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }
    this.metrics.get(name).push({
      duration,
      timestamp: Date.now()
    })

    // 清理性能标记
    performance.clearMarks(`${name}-start`)
    performance.clearMarks(`${name}-end`)
    performance.clearMeasures(name)

    return duration
  }

  // 获取性能指标
  getMetrics(name = null) {
    if (name) {
      return this.metrics.get(name) || []
    }
    
    const result = {}
    for (const [key, values] of this.metrics) {
      const durations = values.map(v => v.duration)
      result[key] = {
        count: values.length,
        average: durations.reduce((a, b) => a + b, 0) / durations.length,
        min: Math.min(...durations),
        max: Math.max(...durations),
        recent: values.slice(-10) // 最近10次
      }
    }
    return result
  }

  // 监控组件渲染性能
  measureComponent(componentName, renderFn) {
    const measureName = `component-${componentName}`
    this.startMeasure(measureName)
    
    return nextTick(() => {
      this.endMeasure(measureName)
    })
  }

  // 监控API请求性能
  measureApiCall(apiName, promise) {
    const measureName = `api-${apiName}`
    this.startMeasure(measureName)
    
    return promise.finally(() => {
      this.endMeasure(measureName)
    })
  }

  // 清理旧指标
  cleanup(maxAge = 3600000) { // 1小时
    const cutoff = Date.now() - maxAge
    
    for (const [name, values] of this.metrics) {
      const filtered = values.filter(v => v.timestamp > cutoff)
      if (filtered.length === 0) {
        this.metrics.delete(name)
      } else {
        this.metrics.set(name, filtered)
      }
    }
  }
}

// 全局性能监控实例
export const performanceMonitor = new PerformanceMonitor()

// 请求合并工具
export class RequestBatcher {
  constructor(delay = 50) {
    this.batches = new Map()
    this.delay = delay
  }

  // 批量请求
  batch(key, requestFn, ...args) {
    return new Promise((resolve, reject) => {
      if (!this.batches.has(key)) {
        this.batches.set(key, {
          requests: [],
          timer: null
        })
      }

      const batch = this.batches.get(key)
      batch.requests.push({ resolve, reject, args })

      // 清除之前的定时器
      if (batch.timer) {
        clearTimeout(batch.timer)
      }

      // 设置新的定时器
      batch.timer = setTimeout(async () => {
        const requests = batch.requests.slice()
        this.batches.delete(key)

        try {
          // 执行批量请求
          const results = await requestFn(requests.map(r => r.args))
          
          // 分发结果
          requests.forEach((request, index) => {
            request.resolve(results[index])
          })
        } catch (error) {
          // 分发错误
          requests.forEach(request => {
            request.reject(error)
          })
        }
      }, this.delay)
    })
  }
}

// 全局请求批处理器
export const requestBatcher = new RequestBatcher()

// 图片懒加载指令
export const lazyLoad = {
  mounted(el, binding) {
    const imageUrl = binding.value
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target
          img.src = imageUrl
          img.classList.remove('lazy-loading')
          img.classList.add('lazy-loaded')
          observer.unobserve(img)
        }
      })
    }, {
      threshold: 0.1
    })

    el.classList.add('lazy-loading')
    observer.observe(el)
  }
}

// 虚拟滚动组合式API
export function useVirtualScroll(items, itemHeight = 50, containerHeight = 400) {
  const scrollTop = ref(0)
  const visibleCount = Math.ceil(containerHeight / itemHeight) + 2
  
  const visibleItems = computed(() => {
    const startIndex = Math.floor(scrollTop.value / itemHeight)
    const endIndex = Math.min(startIndex + visibleCount, items.value.length)
    
    return items.value.slice(startIndex, endIndex).map((item, index) => ({
      ...item,
      index: startIndex + index,
      top: (startIndex + index) * itemHeight
    }))
  })

  const totalHeight = computed(() => items.value.length * itemHeight)
  const offsetY = computed(() => Math.floor(scrollTop.value / itemHeight) * itemHeight)

  const handleScroll = throttle((event) => {
    scrollTop.value = event.target.scrollTop
  }, 16) // 60fps

  return {
    visibleItems,
    totalHeight,
    offsetY,
    handleScroll
  }
}

// 组件懒加载工具
export function lazyLoadComponent(componentImport) {
  return () => ({
    component: componentImport(),
    loading: {
      template: `
        <div class="flex items-center justify-center p-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-2 text-gray-600">加载中...</span>
        </div>
      `
    },
    error: {
      template: `
        <div class="text-center p-8 text-red-600">
          <p>组件加载失败</p>
          <button @click="$parent.$forceUpdate()" class="mt-2 px-4 py-2 bg-red-100 hover:bg-red-200 rounded">
            重试
          </button>
        </div>
      `
    },
    delay: 200,
    timeout: 10000
  })
}

// 缓存管理器
export class CacheManager {
  constructor(maxSize = 100, ttl = 300000) { // 5分钟TTL
    this.cache = new Map()
    this.maxSize = maxSize
    this.ttl = ttl
    this.accessOrder = []
  }

  set(key, value, customTtl = null) {
    const expiresAt = Date.now() + (customTtl || this.ttl)
    
    // 如果已存在，移除旧的访问记录
    if (this.cache.has(key)) {
      const index = this.accessOrder.indexOf(key)
      if (index > -1) {
        this.accessOrder.splice(index, 1)
      }
    }

    // 检查缓存大小限制
    if (this.cache.size >= this.maxSize && !this.cache.has(key)) {
      // 移除最少使用的项
      const lru = this.accessOrder.shift()
      this.cache.delete(lru)
    }

    this.cache.set(key, { value, expiresAt })
    this.accessOrder.push(key)
  }

  get(key) {
    const item = this.cache.get(key)
    
    if (!item) {
      return null
    }

    // 检查是否过期
    if (Date.now() > item.expiresAt) {
      this.delete(key)
      return null
    }

    // 更新访问顺序
    const index = this.accessOrder.indexOf(key)
    if (index > -1) {
      this.accessOrder.splice(index, 1)
      this.accessOrder.push(key)
    }

    return item.value
  }

  delete(key) {
    this.cache.delete(key)
    const index = this.accessOrder.indexOf(key)
    if (index > -1) {
      this.accessOrder.splice(index, 1)
    }
  }

  clear() {
    this.cache.clear()
    this.accessOrder = []
  }

  cleanup() {
    const now = Date.now()
    const keysToDelete = []

    for (const [key, item] of this.cache) {
      if (now > item.expiresAt) {
        keysToDelete.push(key)
      }
    }

    keysToDelete.forEach(key => this.delete(key))
  }

  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      hitRate: this.hitCount / (this.hitCount + this.missCount) || 0
    }
  }
}

// 全局缓存管理器
export const cacheManager = new CacheManager()

// 预加载工具
export class PreloadManager {
  constructor() {
    this.prefetchCache = new Set()
    this.preloadCache = new Set()
  }

  // 预加载资源
  preload(url, type = 'fetch') {
    if (this.preloadCache.has(url)) return

    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = url
    
    switch (type) {
      case 'script':
        link.as = 'script'
        break
      case 'style':
        link.as = 'style'
        break
      case 'image':
        link.as = 'image'
        break
      default:
        link.as = 'fetch'
        link.crossOrigin = 'anonymous'
    }

    document.head.appendChild(link)
    this.preloadCache.add(url)
  }

  // 预获取资源
  prefetch(url) {
    if (this.prefetchCache.has(url)) return

    const link = document.createElement('link')
    link.rel = 'prefetch'
    link.href = url
    document.head.appendChild(link)
    this.prefetchCache.add(url)
  }

  // 预加载路由组件
  preloadRoute(routeName) {
    // 这里需要根据具体的路由配置来实现
    // 示例实现：
    if (window.__ROUTE_COMPONENTS__) {
      const component = window.__ROUTE_COMPONENTS__[routeName]
      if (component && typeof component === 'function') {
        component()
      }
    }
  }
}

// 全局预加载管理器
export const preloadManager = new PreloadManager()

// 错误边界组合式API
export function useErrorBoundary() {
  const error = ref(null)
  const errorInfo = ref(null)

  const catchError = (err, info) => {
    error.value = err
    errorInfo.value = info
    
    // 上报错误
    console.error('组件错误:', err, info)
    
    // 可以在这里添加错误上报逻辑
    if (window.__ERROR_REPORTER__) {
      window.__ERROR_REPORTER__(err, info)
    }
  }

  const clearError = () => {
    error.value = null
    errorInfo.value = null
  }

  return {
    error,
    errorInfo,
    catchError,
    clearError
  }
}

// 自动清理定时器
let cleanupTimer = setInterval(() => {
  performanceMonitor.cleanup()
  cacheManager.cleanup()
}, 300000) // 5分钟清理一次

// 页面卸载时清理
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', () => {
    clearInterval(cleanupTimer)
  })
}

export default {
  debounce,
  throttle,
  performanceMonitor,
  requestBatcher,
  lazyLoad,
  useVirtualScroll,
  lazyLoadComponent,
  cacheManager,
  preloadManager,
  useErrorBoundary
}