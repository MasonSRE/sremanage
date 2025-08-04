<template>
  <div class="performance-metrics">
    <!-- 性能概览卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12a3 3 0 100-6 3 3 0 000 6z"/>
                <path fill-rule="evenodd" d="M9 2a7 7 0 100 14 7 7 0 000-14zm0 12a5 5 0 100-10 5 5 0 000 10z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">24h构建数</p>
            <p class="text-2xl font-semibold text-gray-900">{{ metricsData.overview?.builds24h || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">成功率</p>
            <p class="text-2xl font-semibold text-green-600">{{ metricsData.overview?.overallSuccessRate || 0 }}%</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">队列长度</p>
            <p class="text-2xl font-semibold text-yellow-600">{{ metricsData.overview?.queueLength || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">平均时长</p>
            <p class="text-2xl font-semibold text-purple-600">{{ formatDuration(metricsData.overview?.averageBuildDuration) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制面板 -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-medium text-gray-900">性能监控面板</h3>
      <div class="flex items-center space-x-4">
        <button 
          @click="fetchMetrics"
          :disabled="loading"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          刷新数据
        </button>
        <button 
          @click="runHealthCheck"
          :disabled="healthCheckLoading"
          class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <svg v-if="healthCheckLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          健康检查
        </button>
      </div>
    </div>

    <!-- 预警信息 -->
    <div v-if="metricsData.warnings && metricsData.warnings.length > 0" class="mb-6">
      <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-md">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"/>
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">性能预警</h3>
            <div class="mt-2 text-sm text-yellow-700">
              <ul class="list-disc list-inside space-y-1">
                <li v-for="warning in metricsData.warnings" :key="warning.type">
                  <span :class="[
                    'font-medium',
                    warning.level === 'error' ? 'text-red-600' : 
                    warning.level === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                  ]">
                    {{ warning.message }}
                  </span>
                  <span v-if="warning.suggestion" class="block text-xs mt-1 text-gray-600">
                    建议: {{ warning.suggestion }}
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 健康检查结果 -->
    <div v-if="healthCheckResults" class="mb-6">
      <div class="bg-white rounded-lg shadow">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h4 class="text-lg font-medium text-gray-900">健康检查结果</h4>
            <div class="flex items-center space-x-2">
              <div :class="[
                'w-3 h-3 rounded-full',
                healthCheckResults.overall === 'healthy' ? 'bg-green-400' :
                healthCheckResults.overall === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
              ]"></div>
              <span :class="[
                'text-sm font-medium',
                healthCheckResults.overall === 'healthy' ? 'text-green-600' :
                healthCheckResults.overall === 'warning' ? 'text-yellow-600' : 'text-red-600'
              ]">
                {{ getHealthStatusText(healthCheckResults.overall) }}
              </span>
              <span class="text-sm text-gray-500">(得分: {{ healthCheckResults.score }}/100)</span>
            </div>
          </div>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div v-for="(check, checkName) in healthCheckResults.checks" :key="checkName" 
                 class="border rounded-lg p-4">
              <div class="flex items-center justify-between mb-2">
                <h5 class="text-sm font-medium text-gray-900">{{ getCheckDisplayName(checkName) }}</h5>
                <div :class="[
                  'w-2 h-2 rounded-full',
                  check.status === 'healthy' ? 'bg-green-400' :
                  check.status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
                ]"></div>
              </div>
              <p class="text-xs text-gray-600">{{ check.message }}</p>
              <div v-if="check.responseTime" class="text-xs text-gray-500 mt-1">
                响应时间: {{ check.responseTime }}ms
              </div>
            </div>
          </div>
          <div v-if="healthCheckResults.recommendations && healthCheckResults.recommendations.length > 0" 
               class="mt-4 pt-4 border-t border-gray-200">
            <h5 class="text-sm font-medium text-gray-900 mb-2">建议措施</h5>
            <ul class="text-sm text-gray-600 space-y-1">
              <li v-for="recommendation in healthCheckResults.recommendations" :key="recommendation" 
                  class="flex items-start">
                <span class="mr-2">•</span>
                <span>{{ recommendation }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 性能等级分布 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- 任务性能等级 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">任务性能等级分布</h4>
        <div class="space-y-3">
          <div v-for="(count, level) in metricsData.overview?.performanceLevels" :key="level" 
               class="flex items-center justify-between">
            <div class="flex items-center">
              <div :class="[
                'w-4 h-4 rounded-full mr-3',
                level === 'excellent' ? 'bg-green-500' :
                level === 'good' ? 'bg-blue-500' :
                level === 'fair' ? 'bg-yellow-500' : 'bg-red-500'
              ]"></div>
              <span class="text-sm font-medium text-gray-700">{{ getPerformanceLevelText(level) }}</span>
            </div>
            <span class="text-sm text-gray-900">{{ count }} 个任务</span>
          </div>
        </div>
      </div>

      <!-- 系统信息 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">系统信息</h4>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">Jenkins版本</span>
            <span class="text-sm text-gray-900">{{ metricsData.systemInfo?.jenkinsVersion || 'unknown' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">运行模式</span>
            <span class="text-sm text-gray-900">{{ metricsData.systemInfo?.mode || 'unknown' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">节点描述</span>
            <span class="text-sm text-gray-900">{{ metricsData.systemInfo?.nodeDescription || '-' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">准备关闭</span>
            <span :class="[
              'text-sm',
              metricsData.systemInfo?.quietingDown ? 'text-red-600' : 'text-green-600'
            ]">
              {{ metricsData.systemInfo?.quietingDown ? '是' : '否' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近构建记录 -->
    <div class="bg-white rounded-lg shadow">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">最近构建记录</h4>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">构建号</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">效率</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时长</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="build in metricsData.recentBuilds" :key="`${build.jobName}-${build.number}`" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ build.jobName }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">#{{ build.number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(build.status)">
                  {{ getStatusText(build.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div :class="[
                    'w-2 h-2 rounded-full mr-2',
                    build.efficiency <= 100 ? 'bg-green-400' :
                    build.efficiency <= 150 ? 'bg-yellow-400' : 'bg-red-400'
                  ]"></div>
                  <span class="text-sm text-gray-900">{{ Math.round(build.efficiency) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDuration(build.duration) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ formatTime(build.timestamp) }}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

// Props
const props = defineProps({
  instanceId: {
    type: [String, Number],
    required: true
  }
})

// 响应式数据
const loading = ref(false)
const healthCheckLoading = ref(false)
const metricsData = reactive({
  overview: {},
  jobPerformance: {},
  recentBuilds: [],
  warnings: [],
  systemInfo: {}
})
const healthCheckResults = ref(null)

// 方法
const fetchMetrics = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/metrics/${props.instanceId}`, {
      method: 'GET'
    })
    
    if (response.success) {
      Object.assign(metricsData, response.data)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取性能指标失败:', error)
    notify.error(`获取性能指标失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const runHealthCheck = async () => {
  if (!props.instanceId) return
  
  healthCheckLoading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/health-check/${props.instanceId}`, {
      method: 'POST'
    })
    
    if (response.success) {
      healthCheckResults.value = response.data
      notify.success('健康检查完成')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    notify.error(`健康检查失败: ${error.message}`)
  } finally {
    healthCheckLoading.value = false
  }
}

const formatDuration = (duration) => {
  if (!duration || duration === 0) return '-'
  
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString()
}

const getStatusClass = (status) => {
  const baseClass = 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
  switch (status) {
    case 'success':
      return `${baseClass} bg-green-100 text-green-800`
    case 'failure':
      return `${baseClass} bg-red-100 text-red-800`
    case 'building':
      return `${baseClass} bg-yellow-100 text-yellow-800`
    default:
      return `${baseClass} bg-gray-100 text-gray-800`
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'success':
      return '成功'
    case 'failure':
      return '失败'
    case 'building':
      return '构建中'
    default:
      return '未知'
  }
}

const getHealthStatusText = (status) => {
  switch (status) {
    case 'healthy':
      return '健康'
    case 'warning':
      return '警告'
    case 'unhealthy':
      return '不健康'
    default:
      return '未知'
  }
}

const getCheckDisplayName = (checkName) => {
  const names = {
    connectivity: '连接性',
    system_status: '系统状态',
    queue: '构建队列',
    recent_builds: '最近构建'
  }
  return names[checkName] || checkName
}

const getPerformanceLevelText = (level) => {
  const texts = {
    excellent: '优秀',
    good: '良好',
    fair: '一般',
    poor: '较差'
  }
  return texts[level] || level
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchMetrics()
  }
}, { immediate: true })

// 组件挂载时获取数据
onMounted(() => {
  if (props.instanceId) {
    fetchMetrics()
  }
})
</script>

<style scoped>
.performance-metrics {
  /* 组件特定样式 */
}

/* 悬停效果 */
.hover\:bg-gray-50:hover {
  background-color: #F9FAFB;
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>