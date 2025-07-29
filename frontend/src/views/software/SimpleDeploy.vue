<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页头 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">🚀 简化部署</h1>
            <p class="mt-1 text-sm text-gray-500">直接粘贴 docker-compose.yml 配置，一键部署到服务器</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center text-sm">
              <div :class="aiStatus.ai_available ? 'text-green-600' : 'text-gray-400'">
                🤖 AI助手: {{ aiStatus.ai_available ? '已启用' : '未配置' }}
              </div>
            </div>
            <button @click="refreshData" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- 左侧：部署配置 -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <!-- 基本信息 -->
            <div class="mb-6">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">📝 部署配置</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">实例名称</label>
                  <input
                    v-model="deployForm.instanceName"
                    type="text"
                    placeholder="例如: mysql-prod"
                    class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">目标服务器</label>
                  <select v-model="deployForm.hostId" class="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    <option value="">选择服务器</option>
                    <option v-for="host in hosts" :key="host.id" :value="host.id">
                      {{ host.hostname }} ({{ host.ip }})
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Docker Compose编辑器 -->
            <div class="mb-6">
              <div class="flex justify-between items-center mb-3">
                <h4 class="text-sm font-medium text-gray-700">Docker Compose 配置</h4>
                <button 
                  v-if="aiStatus.ai_available"
                  @click="showAIAssistant = true" 
                  class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  🤖 AI助手
                </button>
              </div>
              
              <textarea
                v-model="deployForm.composeContent"
                rows="20"
                placeholder="粘贴你的 docker-compose.yml 内容

例如：
version: '3.8'
services:
  mysql:
    image: mysql:8.0.30
    container_name: mysql-prod
    environment:
      - MYSQL_ROOT_PASSWORD=dsg238fh8wh3f
      - TZ=Asia/Shanghai
    ports:
      - '3306:3306'
    volumes:
      - ./data:/var/lib/mysql
    restart: unless-stopped"
                class="w-full font-mono text-sm rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 resize-none"
              ></textarea>
              
              <!-- 配置验证状态 -->
              <div v-if="validationResult" class="mt-3">
                <div v-if="validationResult.valid" class="flex items-center text-sm text-green-600">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  配置语法正确
                </div>
                <div v-else class="text-sm text-red-600">
                  <div class="flex items-center mb-1">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    配置有误：
                  </div>
                  <ul class="ml-5 list-disc">
                    <li v-for="error in validationResult.errors" :key="error">{{ error }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <!-- 部署按钮 -->
            <div class="flex justify-end">
              <button
                @click="deployApplication"
                :disabled="!canDeploy || deploying"
                class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="deploying" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ deploying ? '部署中...' : '🚀 开始部署' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 右侧：已部署实例 -->
        <div class="lg:col-span-1">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">📦 已部署实例</h3>
            
            <div v-if="instances.length === 0" class="text-center py-8 text-gray-500">
              <svg class="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
              </svg>
              暂无部署实例
            </div>

            <div v-else class="space-y-3">
              <div 
                v-for="instance in instances" 
                :key="instance.instance_name"
                class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-gray-900">{{ instance.instance_name }}</h4>
                  <span 
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      instance.status === 'running' 
                        ? 'bg-green-100 text-green-800' 
                        : instance.status === 'stopped'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    ]"
                  >
                    {{ instance.status === 'running' ? '运行中' : instance.status === 'stopped' ? '已停止' : instance.status }}
                  </span>
                </div>
                
                <div class="text-xs text-gray-500 mb-3">
                  创建时间: {{ formatDate(instance.created_at) }}
                </div>
                
                <div class="flex space-x-2">
                  <button 
                    v-if="instance.status === 'stopped'"
                    @click="startInstance(instance.instance_name)"
                    class="text-green-600 hover:text-green-700 text-xs"
                    title="启动"
                  >
                    ▶️
                  </button>
                  <button 
                    v-if="instance.status === 'running'"
                    @click="stopInstance(instance.instance_name)"
                    class="text-yellow-600 hover:text-yellow-700 text-xs"
                    title="停止"
                  >
                    ⏸️
                  </button>
                  <button 
                    @click="removeInstance(instance.instance_name)"
                    class="text-red-600 hover:text-red-700 text-xs"
                    title="删除"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- AI助手侧边栏 -->
    <div v-if="showAIAssistant" class="fixed inset-0 bg-black bg-opacity-50 z-50" @click="showAIAssistant = false">
      <div class="fixed right-0 top-0 h-full w-96 bg-white shadow-xl transform transition-transform" @click.stop>
        <!-- AI助手头部 -->
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-semibold">🤖 AI助手</h3>
            <button @click="showAIAssistant = false" class="text-white hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <p class="text-sm opacity-90 mt-1">告诉我你想部署什么应用，我来生成配置</p>
        </div>

        <!-- 聊天区域 -->
        <div class="flex-1 p-4 h-[calc(100vh-180px)] overflow-y-auto">
          <!-- 欢迎消息 -->
          <div class="mb-4 p-3 bg-blue-50 rounded-lg">
            <div class="text-sm text-blue-800">
              👋 你好！我可以帮你生成 docker-compose.yml 配置。
              
              <div class="mt-3 space-y-2">
                <button @click="sendQuickPrompt('MySQL 8.0.30 数据库')" class="block w-full text-left text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                  MySQL数据库
                </button>
                <button @click="sendQuickPrompt('Redis 缓存服务')" class="block w-full text-left text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                  Redis缓存
                </button>
                <button @click="sendQuickPrompt('Nginx 反向代理')" class="block w-full text-left text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">
                  Nginx服务器
                </button>
              </div>
            </div>
          </div>

          <!-- 聊天历史 -->
          <div v-for="message in chatHistory" :key="message.id" class="mb-4">
            <div v-if="message.type === 'user'" class="flex justify-end">
              <div class="bg-blue-600 text-white rounded-lg px-3 py-2 max-w-xs text-sm">
                {{ message.content }}
              </div>
            </div>
            <div v-else class="flex justify-start">
              <div class="bg-gray-100 text-gray-800 rounded-lg px-3 py-2 max-w-xs text-sm">
                <div v-if="message.compose" class="mb-2">
                  {{ message.content }}
                  <pre class="mt-2 bg-gray-800 text-green-400 p-2 rounded text-xs overflow-x-auto">{{ message.compose }}</pre>
                  <button 
                    @click="useAIGenerated(message.compose)"
                    class="mt-2 bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700"
                  >
                    ✅ 使用这个配置
                  </button>
                </div>
                <div v-else>
                  {{ message.content }}
                </div>
              </div>
            </div>
          </div>

          <!-- AI思考中 -->
          <div v-if="aiThinking" class="flex justify-start mb-4">
            <div class="bg-gray-100 text-gray-800 rounded-lg px-3 py-2 max-w-xs text-sm">
              <div class="flex items-center">
                <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                AI正在思考...
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="p-4 border-t">
          <div class="flex">
            <input
              v-model="aiInput"
              type="text"
              placeholder="例如：我要安装MySQL 8.0.30，密码是dsg238fh8wh3f"
              class="flex-1 rounded-l-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
              @keyup.enter="sendToAI"
            />
            <button
              @click="sendToAI"
              :disabled="!aiInput.trim() || aiThinking"
              class="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 部署结果模态框 -->
    <div v-if="showResultModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" @click="showResultModal = false">
      <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto" @click.stop>
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900">部署结果</h3>
            <button @click="showResultModal = false" class="text-gray-400 hover:text-gray-500">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="px-6 py-4">
          <div :class="deployResult.success ? 'text-green-600' : 'text-red-600'" class="mb-4">
            <div class="flex items-center mb-2">
              <svg v-if="deployResult.success" class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              {{ deployResult.message }}
            </div>
          </div>
          
          <div v-if="deployResult.data && deployResult.data.output" class="bg-gray-800 rounded-lg p-4">
            <h4 class="text-white text-sm font-medium mb-2">Docker输出:</h4>
            <pre class="text-green-400 text-xs overflow-x-auto">{{ deployResult.data.output }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchApi } from '@/utils/api'

// 响应式数据
const hosts = ref([])
const instances = ref([])
const aiStatus = ref({ ai_available: false })
const showAIAssistant = ref(false)
const showResultModal = ref(false)
const deploying = ref(false)
const aiThinking = ref(false)

// 表单数据
const deployForm = ref({
  instanceName: '',
  hostId: '',
  composeContent: ''
})

// AI聊天
const aiInput = ref('')
const chatHistory = ref([])
let messageIdCounter = 0

// 部署结果
const deployResult = ref({})
const validationResult = ref(null)

// 计算属性
const canDeploy = computed(() => {
  return deployForm.value.instanceName.trim() && 
         deployForm.value.hostId && 
         deployForm.value.composeContent.trim() &&
         (!validationResult.value || validationResult.value.valid)
})

// 监听compose内容变化进行验证
watch(() => deployForm.value.composeContent, (newContent) => {
  if (newContent.trim()) {
    validateCompose(newContent)
  } else {
    validationResult.value = null
  }
}, { debounce: 500 })

// 方法
const loadHosts = async () => {
  try {
    const response = await fetchApi('/hosts-all-test')
    if (response.success) {
      hosts.value = response.data.map(host => ({
        ...host,
        id: `manual_${host.id}`
      }))
    }
  } catch (error) {
    console.error('获取主机列表失败:', error)
  }
}

const loadInstances = async () => {
  try {
    const response = await fetchApi('/simple-deploy/instances')
    if (response.success) {
      instances.value = response.data
    }
  } catch (error) {
    console.error('获取实例列表失败:', error)
  }
}

const loadAIStatus = async () => {
  try {
    const response = await fetchApi('/simple-deploy/ai/status')
    if (response.success) {
      aiStatus.value = response
    }
  } catch (error) {
    console.error('获取AI状态失败:', error)
  }
}

const validateCompose = async (content) => {
  // 简单的客户端验证
  try {
    if (!content.includes('services:')) {
      validationResult.value = {
        valid: false,
        errors: ['配置必须包含 services 字段']
      }
      return
    }
    
    if (!content.includes('version:')) {
      validationResult.value = {
        valid: false,
        errors: ['建议添加 version 字段']
      }
      return
    }
    
    validationResult.value = { valid: true, errors: [] }
  } catch (error) {
    validationResult.value = {
      valid: false,
      errors: ['配置格式错误']
    }
  }
}

const deployApplication = async () => {
  if (!canDeploy.value) return
  
  deploying.value = true
  
  try {
    const response = await fetchApi('/simple-deploy/deploy', {
      method: 'POST',
      body: {
        instance_name: deployForm.value.instanceName,
        host_id: deployForm.value.hostId,
        compose_content: deployForm.value.composeContent
      }
    })
    
    deployResult.value = response
    showResultModal.value = true
    
    if (response.success) {
      // 清空表单
      deployForm.value = {
        instanceName: '',
        hostId: '',
        composeContent: ''
      }
      validationResult.value = null
      
      // 刷新实例列表
      await loadInstances()
    }
    
  } catch (error) {
    deployResult.value = {
      success: false,
      message: `部署失败: ${error.message}`
    }
    showResultModal.value = true
  }
  
  deploying.value = false
}

const sendToAI = async () => {
  if (!aiInput.value.trim() || aiThinking.value) return
  
  const userMessage = aiInput.value.trim()
  aiInput.value = ''
  
  // 添加用户消息
  chatHistory.value.push({
    id: ++messageIdCounter,
    type: 'user',
    content: userMessage
  })
  
  aiThinking.value = true
  
  try {
    const response = await fetchApi('/simple-deploy/ai/generate', {
      method: 'POST',
      body: { prompt: userMessage }
    })
    
    if (response.success) {
      chatHistory.value.push({
        id: ++messageIdCounter,
        type: 'ai',
        content: response.message,
        compose: response.compose
      })
    } else {
      chatHistory.value.push({
        id: ++messageIdCounter,
        type: 'ai',
        content: `抱歉，生成配置失败: ${response.message}`
      })
    }
  } catch (error) {
    chatHistory.value.push({
      id: ++messageIdCounter,
      type: 'ai',
      content: `抱歉，AI服务暂时不可用: ${error.message}`
    })
  }
  
  aiThinking.value = false
}

const sendQuickPrompt = (prompt) => {
  aiInput.value = prompt
  sendToAI()
}

const useAIGenerated = (composeContent) => {
  deployForm.value.composeContent = composeContent
  showAIAssistant.value = false
}

const startInstance = async (instanceName) => {
  try {
    const response = await fetchApi(`/simple-deploy/instances/${instanceName}/start`, {
      method: 'POST'
    })
    if (response.success) {
      await loadInstances()
    } else {
      alert(`启动失败: ${response.message}`)
    }
  } catch (error) {
    alert(`启动失败: ${error.message}`)
  }
}

const stopInstance = async (instanceName) => {
  if (!confirm(`确定要停止实例 "${instanceName}" 吗？`)) return
  
  try {
    const response = await fetchApi(`/simple-deploy/instances/${instanceName}/stop`, {
      method: 'POST'
    })
    if (response.success) {
      await loadInstances()
    } else {
      alert(`停止失败: ${response.message}`)
    }
  } catch (error) {
    alert(`停止失败: ${error.message}`)
  }
}

const removeInstance = async (instanceName) => {
  if (!confirm(`确定要删除实例 "${instanceName}" 吗？\n\n⚠️ 这将删除所有数据，此操作不可恢复！`)) return
  
  try {
    const response = await fetchApi(`/simple-deploy/instances/${instanceName}/remove`, {
      method: 'DELETE'
    })
    if (response.success) {
      await loadInstances()
    } else {
      alert(`删除失败: ${response.message}`)
    }
  } catch (error) {
    alert(`删除失败: ${error.message}`)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const refreshData = async () => {
  await Promise.all([
    loadHosts(),
    loadInstances(),
    loadAIStatus()
  ])
}

// 组件挂载
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>