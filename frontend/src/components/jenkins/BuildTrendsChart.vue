<template>
  <div class="build-trends-chart">
    <!-- 图表控制面板 -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-medium text-gray-900">构建趋势分析</h3>
      <div class="flex items-center space-x-4">
        <select 
          v-model="selectedInterval" 
          @change="fetchTrends"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="hourly">每小时</option>
          <option value="daily">每天</option>
          <option value="weekly">每周</option>
        </select>
        <select 
          v-model="selectedDays" 
          @change="fetchTrends"
          class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="7">最近7天</option>
          <option value="14">最近14天</option>
          <option value="30">最近30天</option>
          <option value="60">最近60天</option>
        </select>
        <button 
          @click="fetchTrends"
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

    <!-- 趋势图表 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 构建数量趋势 -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-4">构建数量趋势</h4>
          <div ref="buildsChart" class="w-full h-64"></div>
        </div>
        
        <!-- 成功率趋势 -->
        <div>
          <h4 class="text-md font-medium text-gray-900 mb-4">成功率趋势</h4>
          <div ref="successRateChart" class="w-full h-64"></div>
        </div>
      </div>
    </div>

    <!-- 平均构建时长趋势 -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <h4 class="text-md font-medium text-gray-900 mb-4">平均构建时长趋势</h4>
      <div ref="durationChart" class="w-full h-64"></div>
    </div>

    <!-- 趋势摘要 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">时间段数</p>
            <p class="text-2xl font-semibold text-gray-900">{{ trendsData.summary?.totalPeriods || 0 }}</p>
          </div>
        </div>
      </div>

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
            <p class="text-sm font-medium text-gray-500">平均成功率</p>
            <p class="text-2xl font-semibold text-green-600">{{ Math.round(trendsData.summary?.overallSuccessRate || 0) }}%</p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/>
              </svg>
            </div>
          </div>
          <div class="ml-4">
            <p class="text-sm font-medium text-gray-500">平均构建数</p>
            <p class="text-2xl font-semibold text-purple-600">{{ Math.round(trendsData.summary?.averageBuildsPerPeriod || 0) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
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
const selectedInterval = ref('daily')
const selectedDays = ref(30)
const trendsData = reactive({
  trends: [],
  summary: {}
})

// 图表实例
const buildsChart = ref(null)
const successRateChart = ref(null)
const durationChart = ref(null)
let buildsChartInstance = null
let successRateChartInstance = null
let durationChartInstance = null

// 方法
const fetchTrends = async () => {
  if (!props.instanceId) return
  
  loading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/trends/${props.instanceId}`, {
      method: 'GET',
      params: {
        days: selectedDays.value,
        interval: selectedInterval.value
      }
    })
    
    if (response.success) {
      trendsData.trends = response.data.trends || []
      trendsData.summary = response.data.summary || {}
      
      // 更新图表
      await nextTick()
      updateCharts()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取构建趋势数据失败:', error)
    notify.error(`获取构建趋势数据失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const initCharts = () => {
  // 初始化构建数量趋势图
  if (buildsChart.value) {
    buildsChartInstance = echarts.init(buildsChart.value)
  }
  
  // 初始化成功率趋势图
  if (successRateChart.value) {
    successRateChartInstance = echarts.init(successRateChart.value)
  }
  
  // 初始化构建时长趋势图
  if (durationChart.value) {
    durationChartInstance = echarts.init(durationChart.value)
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
}

const updateCharts = () => {
  if (!trendsData.trends.length) return
  
  const timeLabels = trendsData.trends.map(t => t.time)
  
  // 更新构建数量趋势图
  if (buildsChartInstance) {
    const buildsOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['总构建', '成功', '失败', '构建中']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: timeLabels
      },
      yAxis: {
        type: 'value',
        name: '构建数量'
      },
      series: [
        {
          name: '总构建',
          type: 'line',
          data: trendsData.trends.map(t => t.total),
          smooth: true,
          lineStyle: { color: '#3B82F6' },
          itemStyle: { color: '#3B82F6' }
        },
        {
          name: '成功',
          type: 'line',
          data: trendsData.trends.map(t => t.success),
          smooth: true,
          lineStyle: { color: '#10B981' },
          itemStyle: { color: '#10B981' }
        },
        {
          name: '失败',
          type: 'line',
          data: trendsData.trends.map(t => t.failure),
          smooth: true,
          lineStyle: { color: '#EF4444' },
          itemStyle: { color: '#EF4444' }
        },
        {
          name: '构建中',
          type: 'line',
          data: trendsData.trends.map(t => t.building),
          smooth: true,
          lineStyle: { color: '#F59E0B' },
          itemStyle: { color: '#F59E0B' }
        }
      ]
    }
    buildsChartInstance.setOption(buildsOption)
  }
  
  // 更新成功率趋势图
  if (successRateChartInstance) {
    const successRateOption = {
      tooltip: {
        trigger: 'axis',
        formatter: function (params) {
          const dataIndex = params[0].dataIndex
          const data = trendsData.trends[dataIndex]
          return `
            ${params[0].axisValue}<br/>
            成功率: ${data.successRate}%<br/>
            成功: ${data.success} 次<br/>
            失败: ${data.failure} 次<br/>
            总计: ${data.total} 次
          `
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: timeLabels
      },
      yAxis: {
        type: 'value',
        name: '成功率 (%)',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '成功率',
          type: 'line',
          data: trendsData.trends.map(t => t.successRate),
          smooth: true,
          lineStyle: { color: '#10B981' },
          itemStyle: { color: '#10B981' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.1)' }
            ])
          }
        }
      ]
    }
    successRateChartInstance.setOption(successRateOption)
  }
  
  // 更新构建时长趋势图
  if (durationChartInstance) {
    const durationOption = {
      tooltip: {
        trigger: 'axis',
        formatter: function (params) {
          const dataIndex = params[0].dataIndex
          const data = trendsData.trends[dataIndex]
          return `
            ${params[0].axisValue}<br/>
            平均时长: ${formatDuration(data.averageDuration)}<br/>
            构建次数: ${data.total}
          `
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: timeLabels
      },
      yAxis: {
        type: 'value',
        name: '时长 (分钟)',
        axisLabel: {
          formatter: function (value) {
            return Math.round(value / 60000) + 'm'
          }
        }
      },
      series: [
        {
          name: '平均时长',
          type: 'line',
          data: trendsData.trends.map(t => t.averageDuration),
          smooth: true,
          lineStyle: { color: '#8B5CF6' },
          itemStyle: { color: '#8B5CF6' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(139, 92, 246, 0.3)' },
              { offset: 1, color: 'rgba(139, 92, 246, 0.1)' }
            ])
          }
        }
      ]
    }
    durationChartInstance.setOption(durationOption)
  }
}

const formatDuration = (duration) => {
  if (!duration || duration === 0) return '0s'
  
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

const handleResize = () => {
  buildsChartInstance?.resize()
  successRateChartInstance?.resize()
  durationChartInstance?.resize()
}

const disposeCharts = () => {
  buildsChartInstance?.dispose()
  successRateChartInstance?.dispose()
  durationChartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
}

// 监听实例变化
watch(() => props.instanceId, (newId) => {
  if (newId) {
    fetchTrends()
  }
}, { immediate: true })

// 组件挂载时初始化
onMounted(async () => {
  await nextTick()
  initCharts()
  if (props.instanceId) {
    fetchTrends()
  }
})

// 组件卸载时清理资源
onBeforeUnmount(() => {
  disposeCharts()
})
</script>

<style scoped>
.build-trends-chart {
  /* 组件特定样式 */
}

/* 加载状态动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>