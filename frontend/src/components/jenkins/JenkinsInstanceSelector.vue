<template>
  <div class="jenkins-instance-selector">
    <div class="flex items-center space-x-4">
      <label class="text-sm font-medium text-gray-700 flex-shrink-0">
        {{ label }}:
      </label>
      <div class="relative flex-1 max-w-md">
        <select 
          :value="modelValue"
          @change="handleChange"
          :disabled="disabled || loading"
          class="block w-full rounded-md border-gray-300 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="[
            error ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : 'border-gray-300',
            loading ? 'pr-10' : ''
          ]"
        >
          <option value="" disabled>
            {{ placeholder }}
          </option>
          <option 
            v-for="instance in instances" 
            :key="instance.id" 
            :value="instance.id"
          >
            {{ instance.name }}
            <span v-if="showEnvironment && instance.environment" class="text-gray-500">
              ({{ instance.environment }})
            </span>
          </option>
        </select>
        
        <!-- 加载指示器 -->
        <div v-if="loading" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        </div>
      </div>
      
      <!-- 刷新按钮 -->
      <button
        v-if="showRefresh"
        @click="refresh"
        :disabled="loading"
        class="inline-flex items-center p-2 border border-gray-300 rounded-md shadow-sm bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        title="刷新实例列表"
      >
        <svg class="w-4 h-4" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
      </button>
      
      <!-- 添加按钮 -->
      <button
        v-if="showAdd"
        @click="$emit('add')"
        class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        {{ addButtonText }}
      </button>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="mt-1 text-sm text-red-600">
      {{ error }}
    </div>
    
    <!-- 连接状态指示器 -->
    <div v-if="showStatus && selectedInstance" class="mt-2 flex items-center space-x-2 text-sm">
      <div :class="[
        'w-2 h-2 rounded-full',
        connectionStatus === 'connected' ? 'bg-green-400' : 
        connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' : 'bg-red-400'
      ]"></div>
      <span :class="[
        connectionStatus === 'connected' ? 'text-green-600' : 
        connectionStatus === 'connecting' ? 'text-yellow-600' : 'text-red-600'
      ]">
        {{ getStatusText() }}
      </span>
      <span v-if="selectedInstance.url" class="text-gray-500">
        - {{ selectedInstance.url }}
      </span>
    </div>
    
    <!-- 实例统计信息 -->
    <div v-if="showStats && instances.length > 0" class="mt-2 text-xs text-gray-500">
      共 {{ instances.length }} 个实例
      <span v-if="onlineCount !== null">
        (在线: {{ onlineCount }})
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

// Props
const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: '实例'
  },
  placeholder: {
    type: String,
    default: '选择Jenkins实例'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showAdd: {
    type: Boolean,
    default: true
  },
  showStatus: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: false
  },
  showEnvironment: {
    type: Boolean,
    default: false
  },
  addButtonText: {
    type: String,
    default: '添加实例'
  },
  autoLoad: {
    type: Boolean,
    default: true
  },
  autoSelect: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change', 'add', 'refresh', 'error'])

// State
const instances = ref([])
const loading = ref(false)
const error = ref('')
const connectionStatus = ref('disconnected')
const onlineCount = ref(null)

// Computed
const selectedInstance = computed(() => {
  return instances.value.find(instance => instance.id === props.modelValue) || null
})

// Methods
const handleChange = (event) => {
  const value = event.target.value
  const numericValue = value ? parseInt(value) : null
  // 确保类型安全：如果解析失败返回空字符串，成功返回数字
  const safeValue = (numericValue && !isNaN(numericValue)) ? numericValue : ''
  emit('update:modelValue', safeValue)
  emit('change', safeValue, selectedInstance.value)
}

const refresh = async () => {
  await loadInstances()
  emit('refresh')
}

const loadInstances = async () => {
  if (loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'GET'
    })
    
    if (response.success) {
      instances.value = response.data || []
      
      // 自动选择第一个实例
      if (props.autoSelect && instances.value.length > 0 && !props.modelValue) {
        const firstInstance = instances.value[0]
        emit('update:modelValue', firstInstance.id)
        emit('change', firstInstance.id, firstInstance)
      }
      
      // 检查连接状态
      if (props.showStatus && props.modelValue) {
        await checkConnectionStatus()
      }
      
      // 获取在线统计
      if (props.showStats) {
        await updateOnlineStats()
      }
      
    } else {
      throw new Error(response.message || '获取Jenkins实例失败')
    }
  } catch (err) {
    console.error('加载Jenkins实例失败:', err)
    error.value = err.message || '加载失败，请重试'
    emit('error', err)
    
    if (!props.disabled) {
      notify.error(`加载Jenkins实例失败: ${err.message}`)
    }
  } finally {
    loading.value = false
  }
}

const checkConnectionStatus = async () => {
  if (!props.modelValue) {
    connectionStatus.value = 'disconnected'
    return
  }
  
  connectionStatus.value = 'connecting'
  
  try {
    const response = await fetchApi(`/ops/jenkins/test/${props.modelValue}`, {
      method: 'POST'
    })
    
    connectionStatus.value = response.success ? 'connected' : 'disconnected'
  } catch (err) {
    console.error('检查Jenkins连接状态失败:', err)
    connectionStatus.value = 'disconnected'
  }
}

const updateOnlineStats = async () => {
  try {
    const promises = instances.value.map(async (instance) => {
      try {
        const response = await fetchApi(`/ops/jenkins/test/${instance.id}`, {
          method: 'POST'
        })
        return response.success
      } catch {
        return false
      }
    })
    
    const results = await Promise.allSettled(promises)
    onlineCount.value = results.filter(result => 
      result.status === 'fulfilled' && result.value === true
    ).length
  } catch (err) {
    console.error('更新在线统计失败:', err)
  }
}

const getStatusText = () => {
  switch (connectionStatus.value) {
    case 'connected':
      return '已连接'
    case 'connecting':
      return '连接中...'
    case 'disconnected':
    default:
      return '连接断开'
  }
}

// Watchers
watch(() => props.modelValue, async (newValue) => {
  if (props.showStatus && newValue) {
    await checkConnectionStatus()
  }
})

// Lifecycle
onMounted(async () => {
  if (props.autoLoad) {
    await loadInstances()
  }
})

// Expose methods for parent component
defineExpose({
  refresh: loadInstances,
  checkConnection: checkConnectionStatus,
  updateStats: updateOnlineStats
})
</script>

<script>
export default {
  name: 'JenkinsInstanceSelector'
}
</script>

<style scoped>
.jenkins-instance-selector {
  /* 组件特定样式 */
}

/* 加载状态样式 */
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
  .jenkins-instance-selector .flex {
    flex-direction: column;
    align-items: stretch;
    space-y: 2;
  }
  
  .jenkins-instance-selector .space-x-4 > * + * {
    margin-left: 0;
    margin-top: 0.5rem;
  }
}
</style>