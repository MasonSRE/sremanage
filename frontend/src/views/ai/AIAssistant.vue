<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页头 -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">🤖 AI助手</h1>
            <p class="mt-1 text-sm text-gray-500">智能生成Docker配置，简化部署流程</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center text-sm">
              <div :class="aiStatus.ai_available ? 'text-green-600' : 'text-gray-400'">
                <span class="inline-block w-2 h-2 rounded-full mr-2" 
                      :class="aiStatus.ai_available ? 'bg-green-500' : 'bg-gray-400'"></span>
                {{ aiStatus.ai_available ? '服务已启用' : '服务未配置' }}
              </div>
            </div>
            <button @click="refreshAIStatus" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              刷新状态
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- 左侧：AI对话区 -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 h-[600px] flex flex-col">
            <!-- 聊天头部 -->
            <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-t-xl">
              <h3 class="text-lg font-semibold">🤖 智能配置生成器</h3>
              <p class="text-sm opacity-90">告诉我你想部署什么应用，我来生成完整的docker-compose配置</p>
            </div>

            <!-- 聊天区域 -->
            <div class="flex-1 p-4 overflow-y-auto bg-gray-50">
              <!-- 欢迎消息 -->
              <div v-if="chatHistory.length === 0" class="text-center py-8">
                <div class="mb-6">
                  <svg class="mx-auto h-16 w-16 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">👋 欢迎使用AI助手！</h3>
                <p class="text-gray-600 mb-6">我可以帮您生成各种应用的docker-compose配置</p>
                
                <!-- 快速开始按钮 -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-md mx-auto">
                  <button @click="sendQuickPrompt('MySQL 8.0.30 数据库，密码是dsg238fh8wh3f')" 
                          class="p-4 border-2 border-dashed border-blue-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
                    <div class="text-2xl mb-2">🗄️</div>
                    <div class="text-sm font-medium text-blue-600">MySQL数据库</div>
                  </button>
                  <button @click="sendQuickPrompt('Redis 7 缓存服务')" 
                          class="p-4 border-2 border-dashed border-red-300 rounded-lg hover:border-red-500 hover:bg-red-50 transition-colors text-center">
                    <div class="text-2xl mb-2">⚡</div>
                    <div class="text-sm font-medium text-red-600">Redis缓存</div>
                  </button>
                  <button @click="sendQuickPrompt('Nginx 反向代理服务器')" 
                          class="p-4 border-2 border-dashed border-green-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors text-center">
                    <div class="text-2xl mb-2">🌐</div>
                    <div class="text-sm font-medium text-green-600">Nginx服务器</div>
                  </button>
                </div>
              </div>

              <!-- 聊天历史 -->
              <div v-for="message in chatHistory" :key="message.id" class="mb-4">
                <!-- 用户消息 -->
                <div v-if="message.type === 'user'" class="flex justify-end">
                  <div class="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-xs lg:max-w-md">
                    <div class="text-sm">{{ message.content }}</div>
                  </div>
                </div>
                
                <!-- AI消息 -->
                <div v-else class="flex justify-start">
                  <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-xs lg:max-w-md shadow-sm">
                    <div class="text-sm text-gray-800 mb-2">{{ message.content }}</div>
                    
                    <!-- 生成的配置 -->
                    <div v-if="message.compose" class="mt-3">
                      <div class="bg-gray-900 rounded-lg p-3 text-xs overflow-x-auto">
                        <pre class="text-green-400">{{ message.compose }}</pre>
                      </div>
                      
                      <div class="flex space-x-2 mt-3">
                        <button 
                          @click="copyToClipboard(message.compose)"
                          class="flex-1 bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-colors"
                        >
                          📋 复制配置
                        </button>
                        <button 
                          @click="deployConfig(message.compose)"
                          class="flex-1 bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700 transition-colors"
                        >
                          🚀 立即部署
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- AI思考中 -->
              <div v-if="aiThinking" class="flex justify-start mb-4">
                <div class="bg-white border border-gray-200 rounded-lg px-4 py-3 max-w-xs lg:max-w-md shadow-sm">
                  <div class="flex items-center text-sm text-gray-600">
                    <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    AI正在生成配置...
                  </div>
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="p-4 border-t bg-white rounded-b-xl">
              <div class="flex space-x-3">
                <input
                  v-model="userInput"
                  type="text"
                  placeholder="例如：我要安装MySQL 8.0.30，密码是dsg238fh8wh3f，端口3306"
                  class="flex-1 rounded-lg border-gray-300 focus:border-blue-500 focus:ring-blue-500 text-sm"
                  @keyup.enter="sendMessage"
                  :disabled="aiThinking"
                />
                <button
                  @click="sendMessage"
                  :disabled="!userInput.trim() || aiThinking"
                  class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <svg v-if="aiThinking" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span v-else>发送</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：配置面板和快速操作 -->
        <div class="lg:col-span-1 space-y-6">
          
          <!-- AI状态卡片 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">🤖 AI服务状态</h3>
            
            <div v-if="aiStatus.ai_available" class="space-y-3">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">状态</span>
                <span class="text-green-600 font-medium">✅ 已启用</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">模型</span>
                <span class="text-gray-900 font-mono text-xs">{{ aiStatus.model }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">响应速度</span>
                <span class="text-blue-600">🚀 快速</span>
              </div>
            </div>
            
            <div v-else class="text-center py-4">
              <div class="text-gray-400 text-6xl mb-3">🔧</div>
              <h4 class="text-gray-900 font-medium mb-2">AI服务未配置</h4>
              <p class="text-gray-600 text-sm mb-4">在后端配置AI API密钥以启用智能功能</p>
              <div class="bg-gray-50 rounded-lg p-3 text-left">
                <div class="text-xs text-gray-700 font-mono">
                  # backend/.env<br>
                  AI_ENABLED=true<br>
                  AI_API_KEY=your_key<br>
                  AI_MODEL=gpt-4o
                </div>
              </div>
            </div>
          </div>

          <!-- 常用模板 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">📋 常用模板</h3>
            
            <div class="space-y-3">
              <button 
                v-for="template in commonTemplates" 
                :key="template.id"
                @click="sendQuickPrompt(template.prompt)"
                class="w-full flex items-center p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
              >
                <div class="text-2xl mr-3">{{ template.icon }}</div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900">{{ template.name }}</div>
                  <div class="text-xs text-gray-500">{{ template.description }}</div>
                </div>
              </button>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">⚡ 快速操作</h3>
            
            <div class="space-y-3">
              <button 
                @click="clearChat"
                class="w-full flex items-center justify-center p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
              >
                🗑️ 清除对话
              </button>
              <router-link 
                to="/software/simple-deploy" 
                class="w-full flex items-center justify-center p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
              >
                🚀 前往部署页面
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchApi } from '@/utils/api'

const router = useRouter()

// 响应式数据
const aiStatus = ref({ ai_available: false, model: '' })
const chatHistory = ref([])
const userInput = ref('')
const aiThinking = ref(false)
let messageIdCounter = 0

// 常用模板
const commonTemplates = ref([
  {
    id: 'mysql',
    name: 'MySQL数据库',
    description: '关系型数据库服务',
    icon: '🗄️',
    prompt: 'MySQL 8.0.30 数据库，密码是dsg238fh8wh3f，端口3306'
  },
  {
    id: 'redis',
    name: 'Redis缓存',
    description: '高性能缓存服务',
    icon: '⚡',
    prompt: 'Redis 7 缓存服务，端口6379，持久化存储'
  },
  {
    id: 'nginx',
    name: 'Nginx服务器',
    description: 'Web服务器和反向代理',
    icon: '🌐',
    prompt: 'Nginx 反向代理服务器，端口80和443'
  },
  {
    id: 'postgres',
    name: 'PostgreSQL',
    description: '高级关系型数据库',
    icon: '🐘',
    prompt: 'PostgreSQL 15 数据库，密码是postgres123'
  },
  {
    id: 'mongodb',
    name: 'MongoDB',
    description: 'NoSQL文档数据库',
    icon: '🍃',
    prompt: 'MongoDB 7 文档数据库，端口27017'
  },
  {
    id: 'jenkins',
    name: 'Jenkins',
    description: 'CI/CD持续集成',
    icon: '🔨',
    prompt: 'Jenkins CI/CD服务，端口8080，管理员密码admin123'
  }
])

// 方法
const refreshAIStatus = async () => {
  try {
    const response = await fetchApi('/simple-deploy/ai/status')
    if (response.success) {
      aiStatus.value = response
    }
  } catch (error) {
    console.error('获取AI状态失败:', error)
  }
}

const sendMessage = async () => {
  if (!userInput.value.trim() || aiThinking.value) return
  
  const userMessage = userInput.value.trim()
  userInput.value = ''
  
  // 添加用户消息
  chatHistory.value.push({
    id: ++messageIdCounter,
    type: 'user',
    content: userMessage
  })
  
  await generateAIResponse(userMessage)
}

const sendQuickPrompt = async (prompt) => {
  // 添加用户消息
  chatHistory.value.push({
    id: ++messageIdCounter,
    type: 'user',
    content: prompt
  })
  
  await generateAIResponse(prompt)
}

const generateAIResponse = async (prompt) => {
  aiThinking.value = true
  
  try {
    const response = await fetchApi('/simple-deploy/ai/generate', {
      method: 'POST',
      body: { prompt }
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
  
  // 滚动到底部
  setTimeout(() => {
    const chatContainer = document.querySelector('.overflow-y-auto')
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight
    }
  }, 100)
}

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    // 简单的成功提示
    const button = event.target
    const originalText = button.textContent
    button.textContent = '✅ 已复制'
    setTimeout(() => {
      button.textContent = originalText
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
  }
}

const deployConfig = (composeContent) => {
  // 跳转到部署页面并传递配置
  router.push({
    name: 'simple-deploy',
    state: { composeContent }
  })
}

const clearChat = () => {
  if (confirm('确定要清除所有对话记录吗？')) {
    chatHistory.value = []
    messageIdCounter = 0
  }
}

// 组件挂载
onMounted(() => {
  refreshAIStatus()
})
</script>

<style scoped>
/* 聊天滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* 代码块样式优化 */
pre {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>