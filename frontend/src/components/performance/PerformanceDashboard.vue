<template>
  <div class="performance-dashboard">
    <!-- 性能概览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">页面加载时间</p>
            <p class="text-2xl font-semibold text-gray-900">{{ performanceStats.pageLoadTime }}ms</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">API平均响应</p>
            <p class="text-2xl font-semibold text-gray-900">{{ performanceStats.avgApiResponse }}ms</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">组件渲染</p>
            <p class="text-2xl font-semibold text-gray-900">{{ performanceStats.avgComponentRender }}ms</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">缓存命中率</p>
            <p class="text-2xl font-semibold text-gray-900">{{ performanceStats.cacheHitRate }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 性能详情面板 -->
    <div class="bg-white shadow rounded-lg">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6" aria-label="Tabs">
          <button
            @click="activeTab = 'metrics'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'metrics'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📊 性能指标
          </button>
          <button
            @click="activeTab = 'components'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'components'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🧩 组件性能
          </button>
          <button
            @click="activeTab = 'api'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'api'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🌐 API性能
          </button>
          <button
            @click="activeTab = 'optimization'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'optimization'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            ⚡ 优化建议
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- 性能指标面板 -->
        <div v-show="activeTab === 'metrics'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">📊 详细性能指标</h4>
          <div class="space-y-4">
            <div v-for="(metric, name) in performanceMetrics" :key="name" class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h5 class="text-sm font-medium text-gray-900">{{ formatMetricName(name) }}</h5>
                <span class="text-sm text-gray-500">{{ metric.count }} 次调用</span>
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">平均耗时:</span>
                  <span class="ml-1 font-medium">{{ metric.average.toFixed(2) }}ms</span>
                </div>
                <div>
                  <span class="text-gray-500">最小耗时:</span>
                  <span class="ml-1 font-medium">{{ metric.min.toFixed(2) }}ms</span>
                </div>
                <div>
                  <span class="text-gray-500">最大耗时:</span>
                  <span class="ml-1 font-medium">{{ metric.max.toFixed(2) }}ms</span>
                </div>
                <div>
                  <span class="text-gray-500">性能等级:</span>
                  <span :class="[
                    'ml-1 px-2 py-0.5 rounded-full text-xs font-medium',
                    getPerformanceLevel(metric.average)
                  ]">
                    {{ getPerformanceLevelText(metric.average) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 组件性能面板 -->
        <div v-show="activeTab === 'components'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🧩 组件渲染性能</h4>
          <div class="space-y-3">
            <div v-for="component in componentPerformance" :key="component.name" 
                 class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <span class="text-sm font-medium text-gray-900">{{ component.name }}</span>
                <span class="ml-2 text-xs text-gray-500">{{ component.renderCount }} 次渲染</span>
              </div>
              <div class="flex items-center space-x-4">
                <span class="text-sm text-gray-600">{{ component.avgRenderTime }}ms</span>
                <div :class="[
                  'w-3 h-3 rounded-full',
                  component.avgRenderTime < 16 ? 'bg-green-400' : 
                  component.avgRenderTime < 50 ? 'bg-yellow-400' : 'bg-red-400'
                ]"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- API性能面板 -->
        <div v-show="activeTab === 'api'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🌐 API调用性能</h4>
          <div class="space-y-3">
            <div v-for="api in apiPerformance" :key="api.endpoint" 
                 class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-900">{{ api.endpoint }}</span>
                <span class="text-xs text-gray-500">{{ api.callCount }} 次调用</span>
              </div>
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">平均响应:</span>
                  <span class="ml-1 font-medium">{{ api.avgResponseTime }}ms</span>
                </div>
                <div>
                  <span class="text-gray-500">成功率:</span>
                  <span class="ml-1 font-medium">{{ api.successRate }}%</span>
                </div>
                <div>
                  <span class="text-gray-500">错误数:</span>
                  <span class="ml-1 font-medium text-red-600">{{ api.errorCount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 优化建议面板 -->
        <div v-show="activeTab === 'optimization'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">⚡ 性能优化建议</h4>
          <div class="space-y-3">
            <div v-for="(suggestion, index) in optimizationSuggestions" :key="index"
                 class="border-l-4 pl-4 py-3"
                 :class="{
                   'border-red-400 bg-red-50': suggestion.priority === 'high',
                   'border-yellow-400 bg-yellow-50': suggestion.priority === 'medium',
                   'border-blue-400 bg-blue-50': suggestion.priority === 'low'
                 }">
              <div class="flex items-start">
                <div class="flex-shrink-0 mt-0.5">
                  <svg class="w-5 h-5" :class="{
                    'text-red-500': suggestion.priority === 'high',
                    'text-yellow-500': suggestion.priority === 'medium',
                    'text-blue-500': suggestion.priority === 'low'
                  }" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"/>
                  </svg>
                </div>
                <div class="ml-3">
                  <h5 class="text-sm font-medium" :class="{
                    'text-red-800': suggestion.priority === 'high',
                    'text-yellow-800': suggestion.priority === 'medium',
                    'text-blue-800': suggestion.priority === 'low'
                  }">
                    {{ suggestion.title }}
                  </h5>
                  <p class="mt-1 text-sm" :class="{
                    'text-red-700': suggestion.priority === 'high',
                    'text-yellow-700': suggestion.priority === 'medium',
                    'text-blue-700': suggestion.priority === 'low'
                  }">
                    {{ suggestion.description }}
                  </p>
                  <div v-if="suggestion.action" class="mt-2">
                    <button 
                      @click="applySuggestion(suggestion)"
                      class="text-xs px-3 py-1 rounded font-medium"
                      :class="{
                        'bg-red-100 text-red-800 hover:bg-red-200': suggestion.priority === 'high',
                        'bg-yellow-100 text-yellow-800 hover:bg-yellow-200': suggestion.priority === 'medium',
                        'bg-blue-100 text-blue-800 hover:bg-blue-200': suggestion.priority === 'low'
                      }"
                    >
                      {{ suggestion.actionText || '应用建议' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { performanceMonitor, cacheManager } from '@/utils/performance-optimizer'

// 响应式数据
const activeTab = ref('metrics')
const performanceMetrics = ref({})
const performanceStats = ref({
  pageLoadTime: 0,
  avgApiResponse: 0,
  avgComponentRender: 0,
  cacheHitRate: 0
})

// 组件性能数据
const componentPerformance = ref([
  { name: 'Jenkins.vue', renderCount: 15, avgRenderTime: 12.5 },
  { name: 'BuildPredictionAnalysis.vue', renderCount: 8, avgRenderTime: 25.3 },
  { name: 'FailureAnalysis.vue', renderCount: 5, avgRenderTime: 18.7 },
  { name: 'OptimizationRecommendations.vue', renderCount: 6, avgRenderTime: 22.1 }
])

// API性能数据
const apiPerformance = ref([
  { endpoint: '/api/ops/jenkins/jobs', callCount: 23, avgResponseTime: 145, successRate: 98.5, errorCount: 1 },
  { endpoint: '/api/ops/jenkins/prediction', callCount: 12, avgResponseTime: 850, successRate: 100, errorCount: 0 },
  { endpoint: '/api/ops/jenkins/failure-analysis', callCount: 8, avgResponseTime: 1200, successRate: 95.2, errorCount: 2 },
  { endpoint: '/api/performance/metrics', callCount: 15, avgResponseTime: 95, successRate: 100, errorCount: 0 }
])

// 优化建议
const optimizationSuggestions = computed(() => {
  const suggestions = []
  
  // 检查组件渲染性能
  componentPerformance.value.forEach(component => {
    if (component.avgRenderTime > 50) {
      suggestions.push({
        priority: 'high',
        title: `${component.name} 渲染性能问题`,
        description: `组件平均渲染时间 ${component.avgRenderTime}ms，建议优化渲染逻辑`,
        action: () => console.log(`优化 ${component.name}`),
        actionText: '查看详情'
      })
    } else if (component.avgRenderTime > 16) {
      suggestions.push({
        priority: 'medium',
        title: `${component.name} 渲染稍慢`,
        description: `组件渲染时间 ${component.avgRenderTime}ms，可考虑优化`,
        action: () => console.log(`优化 ${component.name}`),
        actionText: '查看详情'
      })
    }
  })
  
  // 检查API性能
  apiPerformance.value.forEach(api => {
    if (api.avgResponseTime > 1000) {
      suggestions.push({
        priority: 'high',
        title: `${api.endpoint} API响应慢`,
        description: `平均响应时间 ${api.avgResponseTime}ms，建议优化或添加缓存`,
        action: () => console.log(`优化 ${api.endpoint}`),
        actionText: '查看详情'
      })
    }
    
    if (api.successRate < 95) {
      suggestions.push({
        priority: 'high',
        title: `${api.endpoint} 错误率高`,
        description: `成功率仅 ${api.successRate}%，需要检查错误原因`,
        action: () => console.log(`检查 ${api.endpoint} 错误`),
        actionText: '查看错误'
      })
    }
  })
  
  // 检查缓存命中率
  if (performanceStats.value.cacheHitRate < 70) {
    suggestions.push({
      priority: 'medium',
      title: '缓存命中率较低',
      description: `当前缓存命中率 ${performanceStats.value.cacheHitRate}%，建议优化缓存策略`,
      action: () => {
        cacheManager.clear()
        refreshPerformanceData()
      },
      actionText: '清空缓存'
    })
  }
  
  if (suggestions.length === 0) {
    suggestions.push({
      priority: 'low',
      title: '性能表现良好',
      description: '当前系统性能指标正常，继续保持监控',
      actionText: '继续监控'
    })
  }
  
  return suggestions.sort((a, b) => {
    const priorities = { high: 3, medium: 2, low: 1 }
    return priorities[b.priority] - priorities[a.priority]
  })
})

// 方法
const formatMetricName = (name) => {
  const nameMap = {
    'component-Jenkins': 'Jenkins主页面',
    'component-BuildPredictionAnalysis': '构建预测分析',
    'component-FailureAnalysis': '失败模式分析',
    'api-jenkins-jobs': 'Jenkins任务列表',
    'api-jenkins-prediction': '构建预测API',
    'api-performance-metrics': '性能指标API'
  }
  return nameMap[name] || name
}

const getPerformanceLevel = (avgTime) => {
  if (avgTime < 100) return 'bg-green-100 text-green-800'
  if (avgTime < 500) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

const getPerformanceLevelText = (avgTime) => {
  if (avgTime < 100) return '优秀'
  if (avgTime < 500) return '良好'
  return '需优化'
}

const applySuggestion = (suggestion) => {
  if (suggestion.action) {
    suggestion.action()
  }
}

const refreshPerformanceData = () => {
  // 获取性能指标
  performanceMetrics.value = performanceMonitor.getMetrics()
  
  // 计算统计数据
  const metrics = Object.values(performanceMetrics.value)
  if (metrics.length > 0) {
    performanceStats.value.avgComponentRender = Math.round(
      metrics.filter(m => m.count > 0)
            .reduce((sum, m) => sum + m.average, 0) / metrics.length
    )
  }
  
  // 模拟页面加载时间
  if (performance.timing) {
    performanceStats.value.pageLoadTime = 
      performance.timing.loadEventEnd - performance.timing.navigationStart
  }
  
  // 计算缓存命中率
  const cacheStats = cacheManager.getStats()
  performanceStats.value.cacheHitRate = Math.round(cacheStats.hitRate * 100)
  
  // 计算API平均响应时间
  const apiAvg = apiPerformance.value.reduce((sum, api) => sum + api.avgResponseTime, 0) / apiPerformance.value.length
  performanceStats.value.avgApiResponse = Math.round(apiAvg)
}

// 定时更新性能数据
let updateInterval = null

onMounted(() => {
  refreshPerformanceData()
  updateInterval = setInterval(refreshPerformanceData, 10000) // 10秒更新一次
})

onBeforeUnmount(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
})
</script>

<style scoped>
.performance-dashboard {
  /* 组件特定样式 */
}

/* 性能等级指示器动画 */
.bg-green-100 {
  animation: pulse-green 2s infinite;
}

.bg-yellow-100 {
  animation: pulse-yellow 2s infinite;
}

.bg-red-100 {
  animation: pulse-red 2s infinite;
}

@keyframes pulse-green {
  0%, 100% { background-color: rgb(220, 252, 231); }
  50% { background-color: rgb(187, 247, 208); }
}

@keyframes pulse-yellow {
  0%, 100% { background-color: rgb(254, 249, 195); }
  50% { background-color: rgb(253, 244, 138); }
}

@keyframes pulse-red {
  0%, 100% { background-color: rgb(254, 226, 226); }
  50% { background-color: rgb(252, 165, 165); }
}
</style>