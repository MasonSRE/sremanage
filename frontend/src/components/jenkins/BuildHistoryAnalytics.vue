<template>
  <div class="build-history-analytics">
    <!-- 统计摘要卡片 -->
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
            <p class="text-sm font-medium text-gray-500">总构建数</p>
            <p class="text-2xl font-semibold text-gray-900">{{ summary.totalBuilds || 0 }}</p>
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
            <p class="text-2xl font-semibold text-green-600">{{ summary.successRate || 0 }}%</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">失败构建</p>
            <p class="text-2xl font-semibold text-red-600">{{ summary.failedBuilds || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">平均时长</p>
            <p class="text-2xl font-semibold text-yellow-600">{{ formatDuration(summary.averageDuration) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 时间范围选择器 -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-medium text-gray-900">构建历史分析</h3>
      <div class="flex items-center space-x-4">
        <select 
          v-model="selectedDays" 
          @change="fetchAnalytics"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="1">最近1天</option>
          <option value="3">最近3天</option>
          <option value="7">最近7天</option>
          <option value="14">最近14天</option>
          <option value="30">最近30天</option>
        </select>
        <button 
          @click="fetchAnalytics"
          :disabled="loading"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          刷新
        </button>
      </div>
    </div>

    <!-- 任务统计表格 -->
    <div class="bg-white shadow rounded-lg mb-6">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">任务统计详情</h4>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">构建次数</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">成功率</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">平均时长</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(stats, jobName) in jobStats" :key="jobName" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ jobName }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ stats.totalBuilds || 0 }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 mr-2">
                    <div :class="[
                      'w-2 h-2 rounded-full',
                      stats.successRate >= 90 ? 'bg-green-400' :
                      stats.successRate >= 70 ? 'bg-yellow-400' : 'bg-red-400'
                    ]"></div>
                  </div>
                  <div class="text-sm text-gray-900">{{ stats.successRate || 0 }}%</div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDuration(stats.averageDuration) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  stats.successRate >= 90 ? 'bg-green-100 text-green-800' :
                  stats.successRate >= 70 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                ]">
                  {{ getStatusText(stats.successRate) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 最近构建记录 -->
    <div class="bg-white shadow rounded-lg">
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
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">触发者</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">时长</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">开始时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="build in builds.slice(0, 20)" :key="build.id" class="hover:bg-gray-50">
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
                <div class="text-sm text-gray-900">{{ build.triggeredBy || 'unknown' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ formatDuration(build.duration) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ formatTime(build.startTime) }}</div>
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
const selectedDays = ref(7)

const summary = reactive({
  totalBuilds: 0,
  successBuilds: 0,
  failedBuilds: 0,
  buildingBuilds: 0,
  successRate: 0,
  averageDuration: 0
})

const jobStats = ref({})
const builds = ref([])

// 方法
const fetchAnalytics = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/${props.instanceId}`, {
      method: 'GET',
      params: {
        days: selectedDays.value,
        limit: 50
      }
    })
    
    if (response.success) {
      const data = response.data
      
      // 更新摘要数据
      Object.assign(summary, data.summary)
      
      // 更新任务统计
      jobStats.value = data.jobStats || {}
      
      // 更新构建记录
      builds.value = data.builds || []
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取构建分析数据失败:', error)
    notify.error(`获取构建分析数据失败: ${error.message}`)
  } finally {
    loading.value = false
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

const getStatusText = (statusOrRate) => {
  if (typeof statusOrRate === 'string') {
    switch (statusOrRate) {
      case 'success':
        return '成功'
      case 'failure':
        return '失败'
      case 'building':
        return '构建中'
      default:
        return '未知'
    }
  } else if (typeof statusOrRate === 'number') {
    if (statusOrRate >= 90) return '优秀'
    if (statusOrRate >= 70) return '良好'
    if (statusOrRate >= 50) return '一般'
    return '较差'
  }
  return '未知'
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchAnalytics()
  }
}, { immediate: true })

// 组件挂载时获取数据
onMounted(() => {
  if (props.instanceId) {
    fetchAnalytics()
  }
})
</script>

<style scoped>
.build-history-analytics {
  /* 组件特定样式 */
}

/* 表格悬停效果 */
.hover\:bg-gray-50:hover {
  background-color: #F9FAFB;
}

/* 加载状态动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>