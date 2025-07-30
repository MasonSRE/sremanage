<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页头 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">批量执行</h1>
            <p class="mt-1 text-sm text-gray-500">选择资产服务器或自定义服务器进行批量操作</p>
          </div>
          <div class="flex items-center space-x-4">
            <button 
              @click="refreshHosts" 
              class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新主机列表
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- 左侧：服务器选择 -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">服务器选择</h3>
            </div>
            
            <div class="p-6">
              <!-- 服务器类型选择 -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">服务器类型</label>
                <div class="space-y-2">
                  <label class="flex items-center">
                    <input 
                      type="radio" 
                      v-model="serverType" 
                      value="asset" 
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">资产服务器</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      type="radio" 
                      v-model="serverType" 
                      value="custom" 
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">自定义服务器</span>
                  </label>
                </div>
              </div>

              <!-- 资产服务器列表 -->
              <div v-if="serverType === 'asset'" class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">选择资产服务器</label>
                <div class="space-y-2 max-h-64 overflow-y-auto">
                  <label 
                    v-for="host in assetHosts" 
                    :key="host.id" 
                    class="flex items-center p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                  >
                    <input 
                      type="checkbox" 
                      v-model="selectedAssetHosts" 
                      :value="host.id"
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <div class="ml-3 flex-1">
                      <div class="text-sm font-medium text-gray-900">{{ host.hostname }}</div>
                      <div class="text-xs text-gray-500">{{ host.ip }}</div>
                      <div class="text-xs text-gray-400">{{ host.source_type === 'aliyun' ? '阿里云ECS' : '手动添加' }}</div>
                    </div>
                    <div class="ml-2">
                      <span :class="[
                        'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        host.status === 'online' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      ]">
                        {{ host.status === 'online' ? '在线' : '离线' }}
                      </span>
                    </div>
                  </label>
                </div>
                
                <!-- 全选控制 -->
                <div class="mt-3 flex items-center justify-between">
                  <button 
                    @click="selectAllAssetHosts"
                    class="text-sm text-blue-600 hover:text-blue-700"
                  >
                    全选 ({{ selectedAssetHosts.length }}/{{ assetHosts.length }})
                  </button>
                  <button 
                    @click="clearAssetSelection"
                    class="text-sm text-gray-600 hover:text-gray-700"
                  >
                    清空选择
                  </button>
                </div>
              </div>

              <!-- 自定义服务器输入 -->
              <div v-if="serverType === 'custom'" class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">自定义服务器</label>
                <textarea
                  v-model="customServers"
                  rows="6"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="每行一个服务器地址，格式：&#10;192.168.1.100&#10;192.168.1.101&#10;server.example.com"
                ></textarea>
                <p class="mt-2 text-xs text-gray-500">每行输入一个服务器IP或域名</p>
              </div>

              <!-- 选中的服务器统计 -->
              <div class="bg-blue-50 rounded-lg p-4">
                <div class="flex items-center">
                  <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <div class="ml-3">
                    <p class="text-sm font-medium text-blue-900">
                      已选择 {{ getSelectedCount() }} 台服务器
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：批量操作 -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">批量操作</h3>
            </div>
            
            <div class="p-6">
              <!-- 命令输入 -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">执行命令</label>
                <textarea
                  v-model="command"
                  rows="4"
                  class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
                  placeholder="输入要批量执行的命令，例如：&#10;ls -la&#10;ps aux | grep nginx&#10;systemctl status nginx"
                ></textarea>
              </div>

              <!-- 执行选项 -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-3">执行选项</label>
                <div class="space-y-3">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="options.parallel" 
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">并行执行（同时在所有服务器上执行）</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="options.continueOnError" 
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">遇到错误继续执行</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="options.showOutput" 
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                    <span class="ml-2 text-sm text-gray-700">实时显示输出</span>
                  </label>
                </div>
              </div>

              <!-- 执行按钮 -->
              <div class="flex justify-end space-x-3">
                <button
                  @click="clearResults"
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  清空结果
                </button>
                <button
                  @click="executeCommand"
                  :disabled="!canExecute || executing"
                  class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  <svg v-if="executing" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ executing ? '执行中...' : '执行命令' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 执行结果 -->
          <div v-if="results.length > 0" class="mt-8 bg-white rounded-xl shadow-sm border border-gray-100">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900">执行结果</h3>
            </div>
            
            <div class="p-6">
              <div class="space-y-4">
                <div 
                  v-for="result in results" 
                  :key="result.host"
                  class="border border-gray-200 rounded-lg overflow-hidden"
                >
                  <div class="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
                    <div class="flex items-center">
                      <span class="font-medium text-gray-900">{{ result.host }}</span>
                      <span :class="[
                        'ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                        result.success 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      ]">
                        {{ result.success ? '成功' : '失败' }}
                      </span>
                    </div>
                    <span class="text-xs text-gray-500">耗时: {{ result.duration }}ms</span>
                  </div>
                  <div class="p-4">
                    <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-900 text-green-400 p-3 rounded">{{ result.output || result.error }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchApi } from '@/utils/api'

// 响应式数据
const serverType = ref('asset')
const assetHosts = ref([])
const selectedAssetHosts = ref([])
const customServers = ref('')
const command = ref('')
const options = ref({
  parallel: true,
  continueOnError: false,
  showOutput: true
})
const executing = ref(false)
const results = ref([])

// 计算属性
const canExecute = computed(() => {
  const hasServers = serverType.value === 'asset' 
    ? selectedAssetHosts.value.length > 0 
    : customServers.value.trim().length > 0
  return hasServers && command.value.trim().length > 0 && !executing.value
})

// 方法
const loadAssetHosts = async () => {
  try {
    const response = await fetchApi('/hosts-all-test')
    if (response.success) {
      assetHosts.value = response.data
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
  }
}

const refreshHosts = () => {
  loadAssetHosts()
}

const selectAllAssetHosts = () => {
  selectedAssetHosts.value = assetHosts.value.map(host => host.id)
}

const clearAssetSelection = () => {
  selectedAssetHosts.value = []
}

const getSelectedCount = () => {
  if (serverType.value === 'asset') {
    return selectedAssetHosts.value.length
  } else {
    return customServers.value.split('\n').filter(line => line.trim()).length
  }
}

const executeCommand = async () => {
  if (!canExecute.value) return
  
  executing.value = true
  results.value = []
  
  try {
    let servers = []
    
    if (serverType.value === 'asset') {
      servers = selectedAssetHosts.value.map(hostId => {
        const host = assetHosts.value.find(h => h.id === hostId)
        return {
          id: hostId,
          host: host?.ip || host?.hostname,
          name: host?.hostname
        }
      })
    } else {
      servers = customServers.value
        .split('\n')
        .filter(line => line.trim())
        .map((host, index) => ({
          id: `custom_${index}`,
          host: host.trim(),
          name: host.trim()
        }))
    }

    const response = await fetchApi('/batch-command', {
      method: 'POST',
      body: {
        servers,
        command: command.value,
        options: options.value
      }
    })

    if (response.success) {
      results.value = response.data.results
    } else {
      alert('执行失败: ' + response.message)
    }
  } catch (error) {
    alert('执行失败: ' + error.message)
  }
  
  executing.value = false
}

const clearResults = () => {
  results.value = []
}

// 组件挂载时加载数据
onMounted(() => {
  loadAssetHosts()
})
</script>

<style scoked>
/* 自定义样式 */
</style>