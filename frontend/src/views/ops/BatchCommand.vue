<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">批量操作</h2>
    </div>

    <!-- 主机选择 -->
    <div class="mb-6">
      <div class="flex justify-between items-center mb-2">
        <label class="text-sm font-medium text-gray-700">选择目标主机</label>
        <span class="text-sm text-gray-500">
          已选择 {{ selectedHosts.length }} 台主机
        </span>
      </div>
      <div class="grid grid-cols-4 gap-4">
        <div v-for="host in hosts" :key="host.id" 
             class="border rounded-lg p-3 cursor-pointer"
             :class="selectedHosts.includes(host.id) ? 'border-blue-500 bg-blue-50' : 'border-gray-200'"
             @click="toggleHost(host.id)">
          <div class="flex items-center">
            <input type="checkbox" 
                   :checked="selectedHosts.includes(host.id)"
                   class="h-4 w-4 text-blue-600 rounded"
                   @change="toggleHost(host.id)"
                   @click.stop>
            <div class="ml-3 flex-1">
              <div class="font-medium">{{ host.hostname }}</div>
              <div class="text-sm text-gray-500">{{ host.ip }}</div>
              <div class="text-xs text-gray-400 mt-1">
                <span :class="[
                  'inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium',
                  host.source_type === 'aliyun' 
                    ? 'bg-orange-100 text-orange-700' 
                    : 'bg-gray-100 text-gray-700'
                ]">
                  {{ host.source_type === 'aliyun' ? '阿里云ECS' : '手动添加' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 命令输入 -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">输入要执行的命令</label>
      <div class="flex">
        <input 
          v-model="command"
          type="text"
          class="flex-1 rounded-l-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          placeholder="输入shell命令"
        >
        <button 
          @click="executeCommand"
          :disabled="!canExecute || isExecuting"
          class="px-4 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          :title="getButtonTitle"
        >
          <svg v-if="isExecuting" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isExecuting ? '执行中...' : '执行' }}
        </button>
      </div>
    </div>

    <!-- 执行结果 -->
    <div v-if="results.length" class="mt-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium">执行结果</h3>
        <div class="text-sm">
          <span class="mr-4">
            <span class="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"></span>
            成功: {{ successCount }}
          </span>
          <span>
            <span class="inline-block w-3 h-3 rounded-full bg-red-500 mr-1"></span>
            失败: {{ failureCount }}
          </span>
        </div>
      </div>
      <div class="space-y-4">
        <div v-for="(result, index) in results" :key="index" 
             :class="['bg-gray-50 rounded-md p-4', result.status === 'error' ? 'border-l-4 border-red-500' : 'border-l-4 border-green-500']">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium">{{ result.hostname }} ({{ result.ip }})</span>
            <span :class="[
              'px-2 py-1 rounded-full text-sm font-medium',
              result.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            ]">
              {{ getStatusText(result.status) }}
            </span>
          </div>
          <pre class="text-sm font-mono whitespace-pre-wrap bg-white p-3 rounded border">{{ result.output || '执行成功' }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchApi } from '@/utils/api'

const hosts = ref([])
const selectedHosts = ref([])
const command = ref('')
const results = ref([])
const isExecuting = ref(false)

// 获取主机列表
const fetchHosts = async () => {
  try {
    const response = await fetchApi('/hosts-all-test')
    console.log('获取到的主机列表:', response)
    if (response.success) {
      hosts.value = response.data
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
  }
}

// 切换主机选择状态
const toggleHost = (hostId) => {
  console.log('切换主机选择:', hostId, '类型:', typeof hostId)
  console.log('当前已选择的主机:', selectedHosts.value)
  
  const index = selectedHosts.value.indexOf(hostId)
  console.log('主机在数组中的索引:', index)
  
  if (index === -1) {
    selectedHosts.value.push(hostId)
    console.log('添加主机到选择列表')
  } else {
    selectedHosts.value.splice(index, 1)
    console.log('从选择列表中移除主机')
  }
  
  console.log('更新后选中的主机:', selectedHosts.value)
  console.log('选中主机数量:', selectedHosts.value.length)
  
  // 立即调用调试函数查看状态
  setTimeout(() => debugCurrentState(), 100)
}

// 判断是否可以执行命令
const canExecute = computed(() => {
  const hasSelectedHosts = selectedHosts.value.length > 0
  const hasCommand = command.value.trim() !== ''
  console.log('执行按钮状态检查:', {
    hasSelectedHosts,
    hasCommand,
    selectedHostsCount: selectedHosts.value.length,
    selectedHosts: selectedHosts.value,
    command: command.value.trim()
  })
  return hasSelectedHosts && hasCommand
})

// 计算成功和失败数量
const successCount = computed(() => results.value.filter(r => r.status === 'success').length)
const failureCount = computed(() => results.value.filter(r => r.status === 'error').length)

// 执行命令
const executeCommand = async () => {
  if (!canExecute.value || isExecuting.value) return
  
  try {
    isExecuting.value = true
    results.value = [] // 清空之前的结果
    
    const response = await fetchApi('/ops/batch-command', {
      method: 'POST',
      body: {
        hosts: selectedHosts.value,
        command: command.value.trim()
      }
    })

    if (response.success) {
      results.value = response.data
    } else {
      throw new Error(response.message || '执行失败')
    }
  } catch (error) {
    console.error('执行命令失败:', error)
    // 显示错误提示
    results.value = [{
      hostname: '系统错误',
      ip: '',
      status: 'error',
      output: error.message
    }]
  } finally {
    isExecuting.value = false
  }
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    success: '执行成功',
    error: '执行失败',
    running: '执行中'
  }
  return texts[status] || '未知状态'
}

// 调试函数 - 检查当前状态
const debugCurrentState = () => {
  console.log('=== 当前状态调试 ===')
  console.log('主机列表数量:', hosts.value.length)
  console.log('选中主机列表:', selectedHosts.value)
  console.log('选中主机数量:', selectedHosts.value.length)
  console.log('主机详情:', hosts.value.map(h => ({ id: h.id, hostname: h.hostname, source: h.source_type })))
  console.log('==================')
}

// 页面加载时获取主机列表
onMounted(async () => {
  console.log('BatchCommand组件已挂载，开始获取主机列表')
  await fetchHosts()
  console.log('主机列表获取完成')
  debugCurrentState()
  
  // 暴露调试函数到全局（仅开发环境）
  if (process.env.NODE_ENV === 'development') {
    window.debugBatchCommand = debugCurrentState
  }
})

const getButtonTitle = computed(() => {
  if (isExecuting.value) return '命令执行中...'
  if (selectedHosts.value.length === 0) return '请选择至少一个主机'
  if (!command.value.trim()) return '请输入要执行的命令'
  return '点击执行命令'
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 