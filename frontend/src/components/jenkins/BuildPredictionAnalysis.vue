<template>
  <div class="build-prediction-analysis">
    <!-- 控制面板 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-medium text-gray-900">🔮 构建预测分析</h3>
        <div class="flex items-center space-x-2">
          <label class="text-sm text-gray-600">任务:</label>
          <select 
            v-model="selectedJob"
            @change="fetchPrediction"
            class="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">全部任务</option>
            <option v-for="job in availableJobs" :key="job" :value="job">{{ job }}</option>
          </select>
        </div>
        <div class="flex items-center space-x-2">
          <label class="text-sm text-gray-600">分析天数:</label>
          <select 
            v-model="selectedDays"
            @change="fetchPrediction"
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
        @click="fetchPrediction"
        :disabled="loading"
        class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        <svg v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        🔄 刷新分析
      </button>
    </div>

    <!-- 预测结果卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <!-- 预计构建时长 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">预计构建时长</p>
            <p class="text-2xl font-semibold text-gray-900">{{ formatDuration(predictionData.prediction?.estimatedDuration) }}</p>
          </div>
        </div>
      </div>

      <!-- 成功概率 -->
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
            <p class="text-sm font-medium text-gray-500">成功概率</p>
            <p class="text-2xl font-semibold text-green-600">{{ predictionData.prediction?.successProbability || 0 }}%</p>
          </div>
        </div>
      </div>

      <!-- 最佳构建时间 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">最佳构建时间</p>
            <p class="text-lg font-semibold text-purple-600">{{ predictionData.prediction?.optimalTime || '未确定' }}</p>
          </div>
        </div>
      </div>

      <!-- 分析置信度 -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">分析置信度</p>
            <p class="text-2xl font-semibold text-yellow-600">{{ predictionData.analysis?.confidence || 0 }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 资源需求预测 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h4 class="text-lg font-medium text-gray-900 mb-4">📊 资源需求预测</h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 rounded-full mr-3" :class="getResourceLevelClass(predictionData.prediction?.resourceRequirement?.cpu)"></div>
            <span class="text-sm font-medium text-gray-700">CPU需求</span>
          </div>
          <span class="text-sm text-gray-900 font-semibold">{{ getResourceLevelText(predictionData.prediction?.resourceRequirement?.cpu) }}</span>
        </div>
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 rounded-full mr-3" :class="getResourceLevelClass(predictionData.prediction?.resourceRequirement?.memory)"></div>
            <span class="text-sm font-medium text-gray-700">内存需求</span>
          </div>
          <span class="text-sm text-gray-900 font-semibold">{{ getResourceLevelText(predictionData.prediction?.resourceRequirement?.memory) }}</span>
        </div>
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 rounded-full mr-3" :class="getResourceLevelClass(predictionData.prediction?.resourceRequirement?.disk)"></div>
            <span class="text-sm font-medium text-gray-700">磁盘需求</span>
          </div>
          <span class="text-sm text-gray-900 font-semibold">{{ getResourceLevelText(predictionData.prediction?.resourceRequirement?.disk) }}</span>
        </div>
      </div>
    </div>

    <!-- 分析详情和建议 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 分析详情 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">📈 分析详情</h4>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">历史数据点</span>
            <span class="text-sm text-gray-900">{{ predictionData.analysis?.historicalDataPoints || 0 }} 个</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">分析时间范围</span>
            <span class="text-sm text-gray-900">{{ predictionData.analysis?.analysisTimeRange || '未知' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">时长变化幅度</span>
            <span class="text-sm text-gray-900">{{ predictionData.analysis?.durationVariance || 0 }}秒</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-500">当前队列长度</span>
            <span class="text-sm text-gray-900">{{ predictionData.analysis?.currentQueueLength || 0 }} 个</span>
          </div>
        </div>
      </div>

      <!-- 智能建议 -->
      <div class="bg-white rounded-lg shadow p-6">
        <h4 class="text-lg font-medium text-gray-900 mb-4">💡 智能建议</h4>
        <div class="space-y-3">
          <div v-if="predictionData.recommendations && predictionData.recommendations.length > 0">
            <div v-for="(recommendation, index) in predictionData.recommendations" :key="index" 
                 class="flex items-start p-3 bg-blue-50 rounded-lg">
              <div class="flex-shrink-0 mt-0.5">
                <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"/>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-blue-800">{{ recommendation }}</p>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            暂无智能建议
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
  },
  availableJobs: {
    type: Array,
    default: () => []
  }
})

// 响应式数据
const loading = ref(false)
const selectedJob = ref('')
const selectedDays = ref(30)
const predictionData = reactive({
  prediction: {
    estimatedDuration: 0,
    successProbability: 0,
    optimalTime: '',
    resourceRequirement: {
      cpu: 'low',
      memory: 'low',
      disk: 'low'
    }
  },
  analysis: {
    historicalDataPoints: 0,
    analysisTimeRange: '',
    confidence: 0,
    durationVariance: 0,
    currentQueueLength: 0
  },
  recommendations: []
})

// 方法
const fetchPrediction = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const params = {
      days: selectedDays.value
    }
    
    if (selectedJob.value) {
      params.job_name = selectedJob.value
    }
    
    const response = await fetchApi(`/ops/jenkins/prediction/${props.instanceId}`, {
      method: 'GET',
      params: params
    })
    
    if (response.success) {
      Object.assign(predictionData, response.data)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取构建预测分析失败:', error)
    notify.error(`获取构建预测分析失败: ${error.message}`)
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

const getResourceLevelClass = (level) => {
  switch (level) {
    case 'low':
      return 'bg-green-400'
    case 'medium':
      return 'bg-yellow-400'
    case 'high':
      return 'bg-red-400'
    default:
      return 'bg-gray-400'
  }
}

const getResourceLevelText = (level) => {
  switch (level) {
    case 'low':
      return '低'
    case 'medium':
      return '中'
    case 'high':
      return '高'
    default:
      return '未知'
  }
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchPrediction()
  }
}, { immediate: true })

// 组件挂载时获取数据
onMounted(() => {
  if (props.instanceId) {
    fetchPrediction()
  }
})
</script>

<style scoped>
.build-prediction-analysis {
  /* 组件特定样式 */
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>