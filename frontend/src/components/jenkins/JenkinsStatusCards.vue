<template>
  <div class="jenkins-status-cards">
    <!-- 加载状态 -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="bg-white overflow-hidden shadow rounded-lg animate-pulse">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-gray-200 rounded-full"></div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <div class="h-4 bg-gray-200 rounded mb-2"></div>
              <div class="h-6 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 状态卡片 -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- 总任务数 -->
      <StatusCard
        title="总任务"
        :value="stats.totalJobs"
        icon="folder"
        color="blue"
        :trend="getTrend('totalJobs')"
        :change="getChange('totalJobs')"
      />

      <!-- 构建中任务 -->
      <StatusCard
        title="构建中"
        :value="stats.buildingJobs"
        icon="building"
        color="yellow"
        :animated="stats.buildingJobs > 0"
        :trend="getTrend('buildingJobs')"
        :change="getChange('buildingJobs')"
      />

      <!-- 队列中任务 -->
      <StatusCard
        title="队列中"
        :value="stats.queueCount"
        icon="clock"
        color="blue"
        :trend="getTrend('queueCount')"
        :change="getChange('queueCount')"
      />

      <!-- 成功率 -->
      <StatusCard
        title="成功率"
        :value="`${stats.successRate}%`"
        icon="check"
        :color="getSuccessRateColor()"
        :trend="getTrend('successRate')"
        :change="getChange('successRate')"
        :show-progress="true"
        :progress-value="stats.successRate"
      />
    </div>

    <!-- 扩展统计信息 -->
    <div v-if="showExtended && !loading" class="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- 平均构建时长 -->
      <StatusCard
        title="平均时长"
        :value="formatDuration(stats.averageDuration)"
        icon="time"
        color="gray"
        size="sm"
      />

      <!-- 今日构建次数 -->
      <StatusCard
        title="今日构建"
        :value="stats.todayBuilds"
        icon="calendar"
        color="green"
        size="sm"
      />

      <!-- 失败任务数 -->
      <StatusCard
        title="失败任务"
        :value="stats.failedJobs"
        icon="exclamation"
        color="red"
        size="sm"
      />
    </div>

    <!-- 刷新时间提示 -->
    <div v-if="!loading && lastUpdate" class="mt-2 text-xs text-gray-500 text-center">
      最后更新: {{ formatTime(lastUpdate) }}
      <span v-if="autoRefresh" class="ml-2 text-green-600">
        (自动刷新中)
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import StatusCard from './StatusCard.vue'

// Props
const props = defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalJobs: 0,
      buildingJobs: 0,
      queueCount: 0,
      successRate: 0,
      failedJobs: 0,
      successJobs: 0,
      averageDuration: 0,
      todayBuilds: 0
    })
  },
  loading: {
    type: Boolean,
    default: false
  },
  showExtended: {
    type: Boolean,
    default: false
  },
  showTrends: {
    type: Boolean,
    default: true
  },
  autoRefresh: {
    type: Boolean,
    default: false
  },
  refreshInterval: {
    type: Number,
    default: 30000
  }
})

// Emits
const emit = defineEmits(['refresh', 'card-click'])

// State
const lastUpdate = ref(null)
const previousStats = ref({})
const refreshTimer = ref(null)

// Methods
const getTrend = (key) => {
  if (!props.showTrends || !previousStats.value[key]) return null
  
  const current = props.stats[key]
  const previous = previousStats.value[key]
  
  if (current > previous) return 'up'
  if (current < previous) return 'down'
  return 'stable'
}

const getChange = (key) => {
  if (!props.showTrends || !previousStats.value[key]) return null
  
  const current = props.stats[key]
  const previous = previousStats.value[key]
  
  return current - previous
}

const getSuccessRateColor = () => {
  const rate = props.stats.successRate
  if (rate >= 80) return 'green'
  if (rate >= 60) return 'yellow'
  return 'red'
}

const formatDuration = (ms) => {
  if (!ms) return '0s'
  
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) return `${hours}h ${minutes % 60}m`
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`
  return `${seconds}s`
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString()
}

const updateStats = () => {
  // 保存之前的统计数据用于趋势计算
  previousStats.value = { ...props.stats }
  lastUpdate.value = Date.now()
}

const startAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
  
  if (props.autoRefresh) {
    refreshTimer.value = setInterval(() => {
      emit('refresh')
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

// Watchers
watch(() => props.stats, (newStats, oldStats) => {
  if (JSON.stringify(newStats) !== JSON.stringify(oldStats)) {
    updateStats()
  }
}, { deep: true })

watch(() => props.autoRefresh, (newValue) => {
  if (newValue) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// Lifecycle
onMounted(() => {
  updateStats()
  if (props.autoRefresh) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})

// Expose methods
defineExpose({
  updateStats,
  startAutoRefresh,
  stopAutoRefresh
})
</script>

<script>
export default {
  name: 'JenkinsStatusCards'
}
</script>

<style scoped>
.jenkins-status-cards {
  /* 组件特定样式 */
}

/* 加载动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .jenkins-status-cards .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .jenkins-status-cards .grid {
    grid-template-columns: 1fr;
  }
}
</style>