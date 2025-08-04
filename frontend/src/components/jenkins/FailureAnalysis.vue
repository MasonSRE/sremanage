<template>
  <div class="failure-analysis">
    <!-- 控制面板 -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center space-x-4">
        <h3 class="text-lg font-medium text-gray-900">🔍 失败模式识别</h3>
        <div class="flex items-center space-x-2">
          <label class="text-sm text-gray-600">任务:</label>
          <select 
            v-model="selectedJob"
            @change="fetchFailureAnalysis"
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
            @change="fetchFailureAnalysis"
            class="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="3">3天</option>
            <option value="7">7天</option>
            <option value="14">14天</option>
            <option value="30">30天</option>
          </select>
        </div>
      </div>
      <button 
        @click="fetchFailureAnalysis"
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
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">失败构建总数</p>
            <p class="text-2xl font-semibold text-red-600">{{ analysisData.analysis?.totalFailures || 0 }}</p>
          </div>
        </div>
      </div>

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
            <p class="text-sm font-medium text-gray-500">分析时间范围</p>
            <p class="text-lg font-semibold text-blue-600">{{ analysisData.analysis?.analysisTimeRange || '未知' }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 01-1.414 1.414L5 6.414V8a1 1 0 01-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 01-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 012 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 010 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 010-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15 13.586V12a1 1 0 011-1z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">失败模式类型</p>
            <p class="text-lg font-semibold text-purple-600">{{ Object.keys(analysisData.analysis?.failurePatterns || {}).length }}</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0112.12 15.12z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">日志分析数</p>
            <p class="text-lg font-semibold text-green-600">{{ analysisData.analysis?.logAnalysisCount || 0 }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 失败模式分析 -->
    <div class="bg-white rounded-lg shadow mb-6" v-if="analysisData.analysis?.failurePatterns && Object.keys(analysisData.analysis.failurePatterns).length > 0">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">🧩 失败模式分析</h4>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="(pattern, key) in analysisData.analysis.failurePatterns" :key="key" 
               class="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-2">
              <h5 class="text-sm font-medium text-gray-900">{{ pattern.name }}</h5>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="pattern.count > 5 ? 'bg-red-100 text-red-800' : pattern.count > 2 ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'">
                {{ pattern.count }} 次
              </span>
            </div>
            <div v-if="pattern.examples && pattern.examples.length > 0" class="space-y-2">
              <div v-for="example in pattern.examples.slice(0, 2)" :key="`${example.jobName}-${example.buildNumber}`"
                   class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                <div class="font-medium">{{ example.jobName }} #{{ example.buildNumber }}</div>
                <div class="mt-1 text-gray-500" v-if="example.excerpt">
                  {{ example.excerpt.length > 100 ? example.excerpt.substring(0, 100) + '...' : example.excerpt }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 常见失败原因 -->
    <div class="bg-white rounded-lg shadow mb-6" v-if="analysisData.analysis?.commonCauses && analysisData.analysis.commonCauses.length > 0">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">📊 常见失败原因</h4>
      </div>
      <div class="p-6">
        <div class="space-y-3">
          <div v-for="cause in analysisData.analysis.commonCauses" :key="cause.cause"
               class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <span class="text-sm text-gray-900">{{ cause.cause || '未知原因' }}</span>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {{ cause.count }} 次
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 解决方案推荐 -->
    <div class="bg-white rounded-lg shadow mb-6" v-if="analysisData.recommendations && analysisData.recommendations.length > 0">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">💡 解决方案推荐</h4>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div v-for="(recommendation, index) in analysisData.recommendations" :key="index"
               class="border-l-4 pl-4 py-2"
               :class="recommendation.priority === 'high' ? 'border-red-400 bg-red-50' : 
                       recommendation.priority === 'medium' ? 'border-yellow-400 bg-yellow-50' : 
                       'border-blue-400 bg-blue-50'">
            <div class="flex items-start">
              <div class="flex-shrink-0 mt-0.5">
                <svg class="w-5 h-5" :class="recommendation.priority === 'high' ? 'text-red-500' : 
                                              recommendation.priority === 'medium' ? 'text-yellow-500' : 'text-blue-500'"
                     fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"/>
                </svg>
              </div>
              <div class="ml-3">
                <h5 class="text-sm font-medium" :class="recommendation.priority === 'high' ? 'text-red-800' : 
                                                       recommendation.priority === 'medium' ? 'text-yellow-800' : 'text-blue-800'">
                  {{ recommendation.type }}
                </h5>
                <p class="mt-1 text-sm" :class="recommendation.priority === 'high' ? 'text-red-700' : 
                                               recommendation.priority === 'medium' ? 'text-yellow-700' : 'text-blue-700'">
                  {{ recommendation.suggestion }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 相似问题检索 -->
    <div class="bg-white rounded-lg shadow" v-if="analysisData.similarIssues && analysisData.similarIssues.length > 0">
      <div class="px-6 py-4 border-b border-gray-200">
        <h4 class="text-lg font-medium text-gray-900">🔗 相似问题检索</h4>
      </div>
      <div class="p-6">
        <div class="space-y-4">
          <div v-for="(issue, index) in analysisData.similarIssues" :key="index"
               class="border rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <h5 class="text-sm font-medium text-gray-900">{{ issue.pattern }}</h5>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                频率: {{ issue.frequency }} 次
              </span>
            </div>
            <p class="text-sm text-gray-600 mb-3">{{ issue.recommendation }}</p>
            <div v-if="issue.recentExamples && issue.recentExamples.length > 0" class="space-y-2">
              <h6 class="text-xs font-medium text-gray-700">最近案例:</h6>
              <div class="space-y-1">
                <div v-for="example in issue.recentExamples" :key="`${example.jobName}-${example.buildNumber}`"
                     class="text-xs text-gray-600 bg-gray-50 p-2 rounded">
                  {{ example.jobName }} #{{ example.buildNumber }} 
                  <span class="text-gray-500">({{ formatTime(example.timestamp) }})</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据状态 -->
    <div v-if="!loading && analysisData.analysis?.totalFailures === 0" 
         class="text-center py-12 bg-white rounded-lg shadow">
      <div class="w-16 h-16 mx-auto mb-4 text-green-400">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" 
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">系统运行稳定</h3>
      <p class="text-gray-500 mb-4">在选定的时间范围内没有发现失败构建</p>
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
const selectedDays = ref(7)
const analysisData = reactive({
  analysis: {
    totalFailures: 0,
    analysisTimeRange: '',
    failurePatterns: {},
    commonCauses: [],
    logAnalysisCount: 0
  },
  recommendations: [],
  similarIssues: []
})

// 方法
const fetchFailureAnalysis = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const params = {
      days: selectedDays.value,
      limit: 20
    }
    
    if (selectedJob.value) {
      params.job_name = selectedJob.value
    }
    
    const response = await fetchApi(`/ops/jenkins/failure-analysis/${props.instanceId}`, {
      method: 'GET',
      params: params
    })
    
    if (response.success) {
      Object.assign(analysisData, response.data)
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取失败模式分析失败:', error)
    notify.error(`获取失败模式分析失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString()
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchFailureAnalysis()
  }
}, { immediate: true })

// 组件挂载时获取数据
onMounted(() => {
  if (props.instanceId) {
    fetchFailureAnalysis()
  }
})
</script>

<style scoped>
.failure-analysis {
  /* 组件特定样式 */
}

/* 加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 过渡动画 */
.transition-shadow {
  transition: box-shadow 0.15s ease-in-out;
}
</style>