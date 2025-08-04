<template>
  <div class="optimization-recommendations">
    <!-- 控制面板 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-medium text-gray-900">⚡ 性能优化建议</h3>
        <div class="flex items-center space-x-2">
          <label class="text-sm text-gray-600">分析天数:</label>
          <select 
            v-model="selectedDays"
            @change="fetchOptimizations"
            class="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="7">7天</option>
            <option value="14">14天</option>
            <option value="30">30天</option>
            <option value="60">60天</option>
          </select>
        </div>
      </div>
      <button 
        @click="fetchOptimizations"
        :disabled="loading"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        🔄 重新分析
      </button>
    </div>

    <!-- 分析概览 -->
    <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
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
            <p class="text-2xl font-semibold text-blue-600">{{ optimizationData.analysis?.totalBuilds || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">任务总数</p>
            <p class="text-2xl font-semibold text-green-600">{{ optimizationData.analysis?.totalJobs || 0 }}</p>
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
            <p class="text-sm font-medium text-gray-500">分析置信度</p>
            <p class="text-2xl font-semibold text-purple-600">{{ optimizationData.analysis?.confidence || 0 }}%</p>
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
            <p class="text-sm font-medium text-gray-500">队列长度</p>
            <p class="text-2xl font-semibold text-yellow-600">{{ optimizationData.analysis?.currentQueueLength || 0 }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0112.12 15.12z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">高峰时段</p>
            <p class="text-lg font-semibold text-red-600">{{ optimizationData.analysis?.peakHours?.length || 0 }}个</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化建议标签页 -->
    <div class="bg-white shadow rounded-lg">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6" aria-label="Tabs">
          <button
            @click="activeTab = 'time'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'time'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🕒 时机优化
          </button>
          <button
            @click="activeTab = 'parallel'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'parallel'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            🔄 并行优化
          </button>
          <button
            @click="activeTab = 'resource'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'resource'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            💾 资源优化
          </button>
          <button
            @click="activeTab = 'summary'"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'summary'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            📋 综合建议
          </button>
        </nav>
      </div>

      <div class="p-6">
        <!-- 时机优化建议 -->
        <div v-show="activeTab === 'time'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">⏰ 最佳构建时机建议</h4>
          <div v-if="optimizationData.optimizations?.timeOptimization && optimizationData.optimizations.timeOptimization.length > 0" 
               class="space-y-4">
            <div v-for="(timeRec, index) in optimizationData.optimizations.timeOptimization" :key="index"
                 class="border rounded-lg p-4 bg-gradient-to-r from-blue-50 to-indigo-50">
              <div class="flex items-center justify-between mb-2">
                <h5 class="text-md font-medium text-gray-900">{{ timeRec.timeSlot }}</h5>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  评分: {{ timeRec.score }}
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ timeRec.reason }}</p>
              <p class="text-sm text-blue-700">💡 {{ timeRec.recommendation }}</p>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            暂无时机优化建议
          </div>
        </div>

        <!-- 并行优化建议 -->
        <div v-show="activeTab === 'parallel'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">🔄 并行构建优化建议</h4>
          <div v-if="optimizationData.optimizations?.parallelOptimization && optimizationData.optimizations.parallelOptimization.length > 0" 
               class="space-y-4">
            <div v-for="(parallelRec, index) in optimizationData.optimizations.parallelOptimization" :key="index"
                 class="border rounded-lg p-4 bg-gradient-to-r from-green-50 to-emerald-50">
              <div class="flex items-center justify-between mb-3">
                <h5 class="text-md font-medium text-gray-900">{{ parallelRec.type }}</h5>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  预计节省: {{ parallelRec.estimated_savings }}
                </span>
              </div>
              <div class="mb-3">
                <p class="text-sm text-gray-600 mb-2">{{ parallelRec.recommendation }}</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="job in parallelRec.jobs.slice(0, 6)" :key="job"
                        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                    {{ job }}
                  </span>
                  <span v-if="parallelRec.jobs.length > 6" 
                        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-200 text-gray-600">
                    +{{ parallelRec.jobs.length - 6 }} 更多...
                  </span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
            </svg>
            暂无并行优化建议
          </div>
        </div>

        <!-- 资源优化建议 -->
        <div v-show="activeTab === 'resource'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">💾 资源配置优化建议</h4>
          <div v-if="optimizationData.optimizations?.resourceOptimization && optimizationData.optimizations.resourceOptimization.length > 0" 
               class="space-y-4">
            <div v-for="(resourceRec, index) in optimizationData.optimizations.resourceOptimization" :key="index"
                 class="border rounded-lg p-4 bg-gradient-to-r from-purple-50 to-pink-50">
              <h5 class="text-md font-medium text-gray-900 mb-2">{{ resourceRec.type }}</h5>
              <p class="text-sm text-gray-600 mb-3">{{ resourceRec.recommendation }}</p>
              
              <!-- 构建效率优化详情 -->
              <div v-if="resourceRec.issues && resourceRec.issues.length > 0" class="space-y-2">
                <h6 class="text-sm font-medium text-gray-700">需要关注的任务:</h6>
                <div class="space-y-2">
                  <div v-for="issue in resourceRec.issues" :key="issue.jobName"
                       class="flex items-center justify-between p-2 bg-white rounded border">
                    <span class="text-sm text-gray-900">{{ issue.jobName }}</span>
                    <div class="flex items-center space-x-2 text-xs text-gray-600">
                      <span>实际: {{ issue.avg_actual }}s</span>
                      <span>预期: {{ issue.avg_estimated }}s</span>
                      <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                            :class="issue.efficiency_ratio > 2 ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'">
                        {{ issue.efficiency_ratio }}x
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 峰值时段信息 -->
              <div v-if="resourceRec.peak_hours && resourceRec.peak_hours.length > 0" class="mt-3">
                <h6 class="text-sm font-medium text-gray-700 mb-2">高峰时段:</h6>
                <div class="flex flex-wrap gap-2">
                  <span v-for="hour in resourceRec.peak_hours" :key="hour"
                        class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-orange-100 text-orange-800">
                    {{ hour }}:00
                  </span>
                </div>
              </div>

              <!-- 当前队列信息 -->
              <div v-if="resourceRec.current_queue" class="mt-3">
                <span class="text-sm text-gray-600">当前队列长度: </span>
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  {{ resourceRec.current_queue }} 个任务
                </span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
            </svg>
            当前资源配置合理
          </div>
        </div>

        <!-- 综合建议 -->
        <div v-show="activeTab === 'summary'">
          <h4 class="text-lg font-medium text-gray-900 mb-4">📋 综合优化建议</h4>
          <div v-if="optimizationData.recommendations && optimizationData.recommendations.length > 0" 
               class="space-y-3">
            <div v-for="(recommendation, index) in optimizationData.recommendations" :key="index"
                 class="flex items-start p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
              <div class="flex-shrink-0 mt-0.5">
                <svg class="w-5 h-5 text-indigo-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"/>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-indigo-800">{{ recommendation }}</p>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            系统运行良好，暂无优化建议
          </div>
        </div>
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
const selectedDays = ref(30)
const activeTab = ref('time')
const optimizationData = reactive({
  optimizations: {
    timeOptimization: [],
    parallelOptimization: [],
    resourceOptimization: []
  },
  analysis: {
    analysisTimeRange: '',
    totalBuilds: 0,
    totalJobs: 0,
    confidence: 0,
    peakHours: [],
    currentQueueLength: 0
  },
  recommendations: []
})

// 方法
const fetchOptimizations = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/optimization-recommendations/${props.instanceId}`, {
      method: 'GET',
      params: {
        days: selectedDays.value
      }
    })
    
    if (response.success) {
      Object.assign(optimizationData, response.data)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取性能优化建议失败:', error)
    notify.error(`获取性能优化建议失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchOptimizations()
  }
}, { immediate: true })

// 组件挂载时获取数据
onMounted(() => {
  if (props.instanceId) {
    fetchOptimizations()
  }
})
</script>

<style scoped>
.optimization-recommendations {
  /* 组件特定样式 */
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 渐变背景 */
.bg-gradient-to-r {
  background: linear-gradient(to right, var(--tw-gradient-stops));
}
</style>