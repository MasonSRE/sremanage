<template>
  <div class="space-y-6">
    <!-- 页面标题和时间范围选择 -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">📈 Jenkins分析报告</h1>
          <p class="mt-1 text-sm text-gray-600">
            深入分析Jenkins构建性能、趋势和优化建议
          </p>
        </div>
        
        <div class="flex items-center space-x-4">
          <select 
            v-model="timeRange"
            @change="refreshAnalytics"
            class="text-sm rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="7d">近7天</option>
            <option value="30d">近30天</option>
            <option value="90d">近90天</option>
            <option value="1y">近1年</option>
          </select>
          
          <button 
            @click="refreshAnalytics"
            :disabled="isLoading"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <svg v-if="isLoading" class="animate-spin -ml-1 mr-1 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            🔄 刷新数据
          </button>
          
          <button 
            @click="exportReport"
            class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            📊 导出报告
          </button>
        </div>
      </div>
    </div>

    <!-- 关键指标概览 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              🚀
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">总构建次数</div>
            <div class="text-2xl font-bold text-gray-900">{{ analytics.totalBuilds || 0 }}</div>
            <div class="flex items-center mt-1">
              <span :class="[
                'text-xs font-medium',
                analytics.buildsChange >= 0 ? 'text-green-600' : 'text-red-600'
              ]">
                {{ analytics.buildsChange >= 0 ? '↑' : '↓' }} {{ Math.abs(analytics.buildsChange || 0) }}%
              </span>
              <span class="text-xs text-gray-500 ml-1">vs 上期</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              ✅
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">成功率</div>
            <div class="text-2xl font-bold text-gray-900">{{ analytics.successRate || 0 }}%</div>
            <div class="flex items-center mt-1">
              <span :class="[
                'text-xs font-medium',
                analytics.successRateChange >= 0 ? 'text-green-600' : 'text-red-600'
              ]">
                {{ analytics.successRateChange >= 0 ? '↑' : '↓' }} {{ Math.abs(analytics.successRateChange || 0) }}%
              </span>
              <span class="text-xs text-gray-500 ml-1">vs 上期</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              ⏱️
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">平均耗时</div>
            <div class="text-2xl font-bold text-gray-900">{{ formatDuration(analytics.avgDuration) }}</div>
            <div class="flex items-center mt-1">
              <span :class="[
                'text-xs font-medium',
                analytics.durationChange <= 0 ? 'text-green-600' : 'text-red-600'
              ]">
                {{ analytics.durationChange <= 0 ? '↓' : '↑' }} {{ Math.abs(analytics.durationChange || 0) }}%
              </span>
              <span class="text-xs text-gray-500 ml-1">vs 上期</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              ⚠️
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">失败次数</div>
            <div class="text-2xl font-bold text-gray-900">{{ analytics.failureCount || 0 }}</div>
            <div class="flex items-center mt-1">
              <span :class="[
                'text-xs font-medium',
                analytics.failureChange <= 0 ? 'text-green-600' : 'text-red-600'
              ]">
                {{ analytics.failureChange <= 0 ? '↓' : '↑' }} {{ Math.abs(analytics.failureChange || 0) }}%
              </span>
              <span class="text-xs text-gray-500 ml-1">vs 上期</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析面板选项卡 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-8 px-6" aria-label="Analytics Tabs">
          <button
            v-for="tab in analyticsTabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              activeTab === tab.id
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </nav>
      </div>
      
      <div class="p-6">
        <!-- 趋势分析 -->
        <div v-show="activeTab === 'trends'">
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2 text-gray-500">加载趋势数据中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-12 text-gray-500">
            请选择Jenkins实例查看趋势分析
          </div>
          <BuildTrendsChart 
            v-else
            :instance-id="selectedInstance" 
            :time-range="timeRange"
          />
        </div>
        
        <!-- 性能分析 -->
        <div v-show="activeTab === 'performance'">
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2 text-gray-500">加载性能数据中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-12 text-gray-500">
            请选择Jenkins实例查看性能分析
          </div>
          <PerformanceMetrics 
            v-else
            :instance-id="selectedInstance"
            :time-range="timeRange" 
          />
        </div>
        
        <!-- 构建历史分析 -->
        <div v-show="activeTab === 'history'">
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2 text-gray-500">加载构建历史中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-12 text-gray-500">
            请选择Jenkins实例查看构建历史
          </div>
          <BuildHistoryAnalytics 
            v-else
            :instance-id="selectedInstance"
            :time-range="timeRange"
          />
        </div>
        
        <!-- 失败分析 -->
        <div v-show="activeTab === 'failures'">
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2 text-gray-500">加载失败分析中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-12 text-gray-500">
            请选择Jenkins实例查看失败分析
          </div>
          <FailureAnalysis 
            v-else
            :instance-id="selectedInstance"
            :time-range="timeRange"
          />
        </div>
        
        <!-- 优化建议 -->
        <div v-show="activeTab === 'optimization'">
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span class="ml-2 text-gray-500">加载优化建议中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-12 text-gray-500">
            请选择Jenkins实例查看优化建议
          </div>
          <OptimizationRecommendations 
            v-else
            :instance-id="selectedInstance"
          />
        </div>
        
        <!-- 自定义报告 -->
        <div v-show="activeTab === 'custom'">
          <div class="space-y-6">
            <div class="bg-gray-50 rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">自定义报告生成器</h3>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">报告类型</label>
                  <select 
                    v-model="customReport.type"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="summary">执行摘要</option>
                    <option value="detailed">详细分析</option>
                    <option value="comparison">对比分析</option>
                    <option value="trend">趋势分析</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">时间范围</label>
                  <select 
                    v-model="customReport.timeRange"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="7d">近7天</option>
                    <option value="30d">近30天</option>
                    <option value="90d">近90天</option>
                    <option value="1y">近1年</option>
                    <option value="custom">自定义范围</option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">包含任务</label>
                  <div class="max-h-32 overflow-y-auto border border-gray-300 rounded-md p-2">
                    <div v-for="job in availableJobs" :key="job" class="flex items-center">
                      <input 
                        type="checkbox"
                        :id="`job-${job}`"
                        :value="job"
                        v-model="customReport.jobs"
                        class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                      >
                      <label :for="`job-${job}`" class="ml-2 text-sm text-gray-700">{{ job }}</label>
                    </div>
                  </div>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">报告格式</label>
                  <div class="space-y-2">
                    <label class="flex items-center">
                      <input type="radio" v-model="customReport.format" value="pdf" class="text-blue-600">
                      <span class="ml-2 text-sm text-gray-700">PDF报告</span>
                    </label>
                    <label class="flex items-center">
                      <input type="radio" v-model="customReport.format" value="excel" class="text-blue-600">
                      <span class="ml-2 text-sm text-gray-700">Excel表格</span>
                    </label>
                    <label class="flex items-center">
                      <input type="radio" v-model="customReport.format" value="json" class="text-blue-600">
                      <span class="ml-2 text-sm text-gray-700">JSON数据</span>
                    </label>
                  </div>
                </div>
              </div>
              
              <div class="mt-6">
                <button 
                  @click="generateCustomReport"
                  :disabled="isLoading || customReport.jobs.length === 0"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <svg v-if="isLoading" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  生成报告
                </button>
              </div>
            </div>
            
            <!-- 报告历史 -->
            <div v-if="reportHistory.length > 0">
              <h3 class="text-lg font-medium text-gray-900 mb-4">报告历史</h3>
              <div class="bg-white border rounded-lg">
                <div class="divide-y divide-gray-200">
                  <div 
                    v-for="report in reportHistory" 
                    :key="report.id"
                    class="p-4 hover:bg-gray-50"
                  >
                    <div class="flex items-center justify-between">
                      <div>
                        <h4 class="text-sm font-medium text-gray-900">{{ report.name }}</h4>
                        <p class="text-xs text-gray-500">
                          生成时间: {{ formatDate(report.createdAt) }} | 
                          类型: {{ report.type }} | 
                          格式: {{ report.format.toUpperCase() }}
                        </p>
                      </div>
                      <div class="flex space-x-2">
                        <button 
                          @click="downloadReport(report)"
                          class="text-sm text-blue-600 hover:text-blue-800"
                        >
                          下载
                        </button>
                        <button 
                          @click="deleteReport(report)"
                          class="text-sm text-red-600 hover:text-red-800"
                        >
                          删除
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
    </div>

    <!-- 快捷洞察 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 最活跃的任务 -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">🔥 最活跃任务</h3>
        <div class="space-y-3">
          <div v-for="job in topActiveJobs" :key="job.name" class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span class="text-sm font-medium text-gray-900">{{ job.name }}</span>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-900">{{ job.buildCount }} 次构建</div>
              <div class="text-xs text-gray-500">{{ job.successRate }}% 成功率</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最耗时的任务 -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">⏱️ 最耗时任务</h3>
        <div class="space-y-3">
          <div v-for="job in topSlowJobs" :key="job.name" class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span class="text-sm font-medium text-gray-900">{{ job.name }}</span>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-900">{{ formatDuration(job.avgDuration) }}</div>
              <div class="text-xs text-gray-500">平均耗时</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 最常失败的任务 -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">❌ 问题任务</h3>
        <div class="space-y-3">
          <div v-for="job in topFailedJobs" :key="job.name" class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-red-500 rounded-full"></div>
              <span class="text-sm font-medium text-gray-900">{{ job.name }}</span>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-900">{{ job.failureRate }}% 失败率</div>
              <div class="text-xs text-gray-500">{{ job.failureCount }} 次失败</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 改进建议 -->
      <div class="bg-white rounded-lg shadow-sm border p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">💡 改进建议</h3>
        <div class="space-y-3">
          <div v-for="suggestion in improvementSuggestions" :key="suggestion.id" class="flex items-start space-x-3">
            <div class="flex-shrink-0 w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div>
              <div class="text-sm font-medium text-gray-900">{{ suggestion.title }}</div>
              <div class="text-xs text-gray-500">{{ suggestion.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, inject, watch } from 'vue'
import BuildTrendsChart from '@/components/jenkins/BuildTrendsChart.vue'
import PerformanceMetrics from '@/components/jenkins/PerformanceMetrics.vue'
import BuildHistoryAnalytics from '@/components/jenkins/BuildHistoryAnalytics.vue'
import FailureAnalysis from '@/components/jenkins/FailureAnalysis.vue'
import OptimizationRecommendations from '@/components/jenkins/OptimizationRecommendations.vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

// 注入全局状态
const selectedInstance = inject('jenkinsInstance')

// 响应式状态
const isLoading = ref(false)
const timeRange = ref('30d')
const activeTab = ref('trends')

// 分析数据
const analytics = ref({
  totalBuilds: 0,
  successRate: 0,
  avgDuration: 0,
  failureCount: 0,
  buildsChange: 0,
  successRateChange: 0,
  durationChange: 0,
  failureChange: 0
})

// 洞察数据
const topActiveJobs = ref([])
const topSlowJobs = ref([])
const topFailedJobs = ref([])
const improvementSuggestions = ref([])

// 自定义报告
const customReport = ref({
  type: 'summary',
  timeRange: '30d',
  jobs: [],
  format: 'pdf'
})

const availableJobs = ref([])
const reportHistory = ref([])

// 分析选项卡
const analyticsTabs = [
  { id: 'trends', label: '趋势分析', icon: '📈' },
  { id: 'performance', label: '性能分析', icon: '⚡' },
  { id: 'history', label: '构建分析', icon: '📋' },
  { id: 'failures', label: '失败分析', icon: '🔍' },
  { id: 'optimization', label: '优化建议', icon: '💡' },
  { id: 'custom', label: '自定义报告', icon: '📊' }
]

// 方法
const formatDuration = (ms) => {
  if (!ms) return '0秒'
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes % 60}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds % 60}秒`
  } else {
    return `${seconds}秒`
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString()
}

const refreshAnalytics = async () => {
  if (!selectedInstance.value) return
  
  isLoading.value = true
  try {
    await Promise.all([
      fetchAnalyticsOverview(),
      fetchTopJobs(),
      fetchImprovementSuggestions(),
      fetchAvailableJobs()
    ])
  } catch (error) {
    console.error('刷新分析数据失败:', error)
    notify.error(`刷新分析数据失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const fetchAnalyticsOverview = async () => {
  try {
    const params = new URLSearchParams({
      timeRange: timeRange.value
    })
    
    const response = await fetchApi(`/ops/jenkins/analytics/overview/${selectedInstance.value}?${params}`, {
      method: 'GET'
    })
    
    if (response.success) {
      analytics.value = response.data
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取分析概览失败:', error)
    notify.error(`获取分析概览失败: ${error.message}`)
  }
}

const fetchTopJobs = async () => {
  try {
    const params = new URLSearchParams({
      timeRange: timeRange.value
    })
    
    const response = await fetchApi(`/ops/jenkins/analytics/top-jobs/${selectedInstance.value}?${params}`, {
      method: 'GET'
    })
    
    if (response.success) {
      topActiveJobs.value = response.data.mostActive || []
      topSlowJobs.value = response.data.slowest || []
      topFailedJobs.value = response.data.mostFailed || []
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取热门任务失败:', error)
    notify.error(`获取热门任务失败: ${error.message}`)
  }
}

const fetchImprovementSuggestions = async () => {
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/suggestions/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      improvementSuggestions.value = response.data || []
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取改进建议失败:', error)
    notify.error(`获取改进建议失败: ${error.message}`)
  }
}

const fetchAvailableJobs = async () => {
  try {
    const response = await fetchApi(`/ops/jenkins/jobs/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      availableJobs.value = response.data.map(job => job.name)
      // 默认选择所有任务
      if (customReport.value.jobs.length === 0) {
        customReport.value.jobs = [...availableJobs.value]
      }
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取可用任务失败:', error)
    notify.error(`获取可用任务失败: ${error.message}`)
  }
}

const generateCustomReport = async () => {
  if (!selectedInstance.value || customReport.value.jobs.length === 0) {
    notify.warning('请选择要包含在报告中的任务')
    return
  }
  
  isLoading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/custom-report/${selectedInstance.value}`, {
      method: 'POST',
      body: {
        type: customReport.value.type,
        timeRange: customReport.value.timeRange,
        jobs: customReport.value.jobs,
        format: customReport.value.format
      }
    })
    
    if (response.success) {
      notify.success('报告生成成功')
      
      // 如果是文件下载
      if (response.data.downloadUrl) {
        const link = document.createElement('a')
        link.href = response.data.downloadUrl
        link.download = response.data.filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
      
      // 刷新报告历史
      await fetchReportHistory()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('生成报告失败:', error)
    notify.error(`生成报告失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const fetchReportHistory = async () => {
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/reports/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      reportHistory.value = response.data || []
    }
  } catch (error) {
    console.error('获取报告历史失败:', error)
  }
}

const downloadReport = async (report) => {
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/reports/${selectedInstance.value}/${report.id}/download`, {
      method: 'GET'
    })
    
    if (response.success && response.data.downloadUrl) {
      const link = document.createElement('a')
      link.href = response.data.downloadUrl
      link.download = report.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (error) {
    console.error('下载报告失败:', error)
    notify.error(`下载报告失败: ${error.message}`)
  }
}

const deleteReport = async (report) => {
  if (!(await notify.confirm(`确定要删除报告 "${report.name}" 吗？`))) {
    return
  }
  
  try {
    const response = await fetchApi(`/ops/jenkins/analytics/reports/${selectedInstance.value}/${report.id}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      notify.success('报告删除成功')
      await fetchReportHistory()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('删除报告失败:', error)
    notify.error(`删除报告失败: ${error.message}`)
  }
}

const exportReport = () => {
  // 导出当前分析数据
  const reportData = {
    instance: selectedInstance.value,
    timeRange: timeRange.value,
    generatedAt: new Date().toISOString(),
    analytics: analytics.value,
    topJobs: {
      mostActive: topActiveJobs.value,
      slowest: topSlowJobs.value,
      mostFailed: topFailedJobs.value
    },
    suggestions: improvementSuggestions.value
  }
  
  const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `jenkins-analytics-${selectedInstance.value}-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
  
  notify.success('报告导出成功')
}

// 监听实例变化
watch(selectedInstance, async (newInstance) => {
  if (newInstance) {
    await refreshAnalytics() 
    await fetchReportHistory()
  } else {
    // 清空数据当实例为空时
    analytics.value = {
      totalBuilds: 0,
      successRate: 0,
      avgDuration: 0,
      failureCount: 0,
      buildsChange: 0,
      successRateChange: 0,
      durationChange: 0,
      failureChange: 0
    }
    topActiveJobs.value = []
    topSlowJobs.value = []
    topFailedJobs.value = []
    improvementSuggestions.value = []
    availableJobs.value = []
    reportHistory.value = []
  }
}, { immediate: true })

// 初始化
onMounted(async () => {
  // 监听全局刷新事件
  window.addEventListener('jenkins-refresh', refreshAnalytics)
})

onBeforeUnmount(() => {
  window.removeEventListener('jenkins-refresh', refreshAnalytics)
})
</script>

<style scoped>
/* 趋势指示器 */
.trend-up {
  @apply text-green-600;
}

.trend-down {
  @apply text-red-600;
}

/* 选项卡激活状态 */
.tab-active {
  @apply border-blue-500 text-blue-600;
}

/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .md\:grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\:grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>