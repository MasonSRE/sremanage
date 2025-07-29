<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
    <!-- 页头 -->
    <div class="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div>
            <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🔧 SRE助手
            </h1>
            <p class="mt-1 text-sm text-gray-600">Site Reliability Engineering智能助手，助力系统可靠性提升</p>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center text-sm">
              <div :class="systemStatus.healthy ? 'text-green-600' : 'text-orange-500'">
                <span class="inline-block w-2 h-2 rounded-full mr-2 animate-pulse" 
                      :class="systemStatus.healthy ? 'bg-green-500' : 'bg-orange-500'"></span>
                {{ systemStatus.healthy ? '系统健康' : '需要关注' }}
              </div>
            </div>
            <button @click="refreshSystemStatus" 
                    class="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg">
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
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        <!-- 左侧：AI对话区 -->
        <div class="lg:col-span-3">
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 h-[600px] flex flex-col">
            <!-- 聊天头部 -->
            <div class="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white p-4 rounded-t-xl">
              <h3 class="text-lg font-semibold flex items-center">
                <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                SRE智能顾问
              </h3>
              <p class="text-sm opacity-90">专业的SRE咨询服务，涵盖故障排查、性能优化、监控告警等各个方面</p>
            </div>

            <!-- 聊天区域 -->
            <div class="flex-1 p-4 overflow-y-auto" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);">
              <!-- 欢迎消息 -->
              <div v-if="chatHistory.length === 0" class="text-center py-8">
                <div class="mb-6">
                  <div class="mx-auto h-20 w-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                    <svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                  </div>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">👋 欢迎使用SRE助手！</h3>
                <p class="text-gray-600 mb-8">我是您的专业SRE顾问，随时为您提供技术支持和最佳实践建议</p>
                
                <!-- SRE场景按钮 -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-4xl mx-auto">
                  <button @click="sendQuickPrompt('系统出现高延迟，请帮我分析可能的原因和排查步骤')" 
                          class="sre-scenario-btn bg-red-50 border-red-200 hover:border-red-400 hover:bg-red-100">
                    <div class="text-3xl mb-3">🚨</div>
                    <div class="text-sm font-medium text-red-700">故障排查</div>
                    <div class="text-xs text-red-600 mt-1">快速定位问题</div>
                  </button>
                  
                  <button @click="sendQuickPrompt('我需要制定系统监控策略，包括关键指标和告警规则')" 
                          class="sre-scenario-btn bg-blue-50 border-blue-200 hover:border-blue-400 hover:bg-blue-100">
                    <div class="text-3xl mb-3">📊</div>
                    <div class="text-sm font-medium text-blue-700">监控告警</div>
                    <div class="text-xs text-blue-600 mt-1">完善监控体系</div>
                  </button>
                  
                  <button @click="sendQuickPrompt('帮我优化系统性能，目前响应时间较慢')" 
                          class="sre-scenario-btn bg-green-50 border-green-200 hover:border-green-400 hover:bg-green-100">
                    <div class="text-3xl mb-3">⚡</div>
                    <div class="text-sm font-medium text-green-700">性能优化</div>
                    <div class="text-xs text-green-600 mt-1">提升系统效率</div>
                  </button>
                  
                  <button @click="sendQuickPrompt('需要制定灾难恢复计划，确保业务连续性')" 
                          class="sre-scenario-btn bg-purple-50 border-purple-200 hover:border-purple-400 hover:bg-purple-100">
                    <div class="text-3xl mb-3">🛡️</div>
                    <div class="text-sm font-medium text-purple-700">灾难恢复</div>
                    <div class="text-xs text-purple-600 mt-1">业务连续性</div>
                  </button>
                </div>

                <!-- 快速咨询 -->
                <div class="mt-8 text-left max-w-md mx-auto">
                  <h4 class="text-sm font-semibold text-gray-700 mb-3">💡 常见咨询：</h4>
                  <div class="space-y-2">
                    <button @click="sendQuickPrompt('如何设计高可用架构？')" 
                            class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      • 如何设计高可用架构？
                    </button>
                    <button @click="sendQuickPrompt('制定SLA和SLO的最佳实践是什么？')" 
                            class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      • 制定SLA和SLO的最佳实践
                    </button>
                    <button @click="sendQuickPrompt('容量规划应该如何进行？')" 
                            class="w-full text-left px-3 py-2 text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                      • 容量规划应该如何进行？
                    </button>
                  </div>
                </div>
              </div>

              <!-- 聊天历史 -->
              <div v-for="message in chatHistory" :key="message.id" class="mb-6">
                <!-- 用户消息 -->
                <div v-if="message.type === 'user'" class="flex justify-end">
                  <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl px-4 py-3 max-w-xs lg:max-w-md shadow-md">
                    <div class="text-sm">{{ message.content }}</div>
                  </div>
                </div>
                
                <!-- AI消息 -->
                <div v-else class="flex justify-start">
                  <div class="bg-white border border-gray-200/50 rounded-2xl px-4 py-4 max-w-xs lg:max-w-lg shadow-sm">
                    <div class="flex items-start space-x-3">
                      <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                        </svg>
                      </div>
                      <div class="flex-1">
                        <!-- 流式输出指示器 -->
                        <div v-if="message.streaming" class="flex items-center text-xs text-blue-600 mb-2">
                          <svg class="animate-pulse h-3 w-3 mr-1" fill="currentColor" viewBox="0 0 8 8">
                            <circle cx="4" cy="4" r="3"></circle>
                          </svg>
                          正在分析...
                        </div>
                        
                        <!-- AI回复内容 - 支持markdown -->
                        <div 
                          class="text-sm text-gray-800 leading-relaxed markdown-content"
                          v-html="renderMarkdown(message.content)"
                        ></div>
                        
                        <!-- 如果有建议或步骤 -->
                        <div v-if="message.suggestions" class="mt-4">
                          <div class="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3">
                            <h5 class="text-xs font-semibold text-gray-700 mb-2">📋 建议步骤：</h5>
                            <ul class="text-xs text-gray-600 space-y-1">
                              <li v-for="suggestion in message.suggestions" :key="suggestion" class="flex items-start">
                                <span class="text-blue-500 mr-2">•</span>
                                <span v-html="renderMarkdown(suggestion)"></span>
                              </li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- AI思考中 -->
              <div v-if="aiThinking" class="flex justify-start mb-4">
                <div class="bg-white border border-gray-200/50 rounded-2xl px-4 py-4 max-w-xs lg:max-w-md shadow-sm">
                  <div class="flex items-center text-sm text-gray-600">
                    <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-3">
                      <svg class="animate-spin h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                    SRE助手正在分析中...
                  </div>
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="p-4 border-t border-gray-200/50 bg-white/50 backdrop-blur-sm rounded-b-xl">
              <div class="flex space-x-3">
                <textarea
                  v-model="userInput"
                  placeholder="描述您遇到的问题或需要的建议，例如：系统出现高延迟，如何排查？&#10;&#10;💡 提示：Shift+Enter 换行，Enter 发送"
                  class="flex-1 rounded-lg border-gray-200 focus:border-blue-500 focus:ring-blue-500 text-sm bg-white/80 backdrop-blur-sm resize-none"
                  rows="2"
                  @keydown="handleKeyDown"
                  @compositionstart="isComposing = true"
                  @compositionend="isComposing = false"
                  :disabled="aiThinking"
                ></textarea>
                <button
                  @click="sendMessage"
                  :disabled="!userInput.trim() || aiThinking"
                  class="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
                >
                  <svg v-if="aiThinking" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span v-else>咨询</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：工具面板 -->
        <div class="lg:col-span-1 space-y-6">
          
          <!-- 系统状态概览 -->
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              系统概览
            </h3>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">总体健康度</span>
                <div class="flex items-center">
                  <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span class="text-sm font-medium text-green-600">良好</span>
                </div>
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between text-xs text-gray-600">
                  <span>CPU使用率</span>
                  <span>65%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div class="bg-blue-600 h-1.5 rounded-full" style="width: 65%"></div>
                </div>
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between text-xs text-gray-600">
                  <span>内存使用率</span>
                  <span>78%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div class="bg-orange-500 h-1.5 rounded-full" style="width: 78%"></div>
                </div>
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between text-xs text-gray-600">
                  <span>服务可用性</span>
                  <span>99.9%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1.5">
                  <div class="bg-green-500 h-1.5 rounded-full" style="width: 99.9%"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- SRE工具箱 -->
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
              </svg>
              SRE工具箱
            </h3>
            
            <div class="space-y-3">
              <button 
                v-for="tool in sreTools" 
                :key="tool.id"
                @click="sendQuickPrompt(tool.prompt)"
                class="w-full flex items-center p-3 border border-gray-200/50 rounded-lg hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-200 text-left group"
              >
                <div class="text-xl mr-3 group-hover:scale-110 transition-transform">{{ tool.icon }}</div>
                <div class="flex-1">
                  <div class="text-sm font-medium text-gray-900">{{ tool.name }}</div>
                  <div class="text-xs text-gray-500">{{ tool.description }}</div>
                </div>
              </button>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">⚡ 快速操作</h3>
            
            <div class="space-y-3">
              <button 
                @click="clearChat"
                class="w-full flex items-center justify-center p-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm text-gray-700"
              >
                🗑️ 清除对话
              </button>
              <button 
                @click="exportChatHistory"
                class="w-full flex items-center justify-center p-2 border border-blue-300 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors text-sm"
              >
                📄 导出记录
              </button>
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
import { marked } from 'marked'
import 'highlight.js/styles/github-dark.css'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import yaml from 'highlight.js/lib/languages/yaml'
import bash from 'highlight.js/lib/languages/bash'

// 注册语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('yaml', yaml)
hljs.registerLanguage('bash', bash)

// 配置marked
marked.setOptions({
  highlight: function(code, language) {
    if (language && hljs.getLanguage(language)) {
      try {
        return hljs.highlight(code, { language }).value
      } catch (err) {}
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true
})

const router = useRouter()

// 响应式数据
const systemStatus = ref({ healthy: true })
const chatHistory = ref([])
const userInput = ref('')
const aiThinking = ref(false)
const isComposing = ref(false) // 输入法组合状态
let messageIdCounter = 0

// SRE工具
const sreTools = ref([
  {
    id: 'runbook',
    name: '故障手册',
    description: '常见问题解决方案',
    icon: '📖',
    prompt: '为我生成一个完整的故障排查手册，包括常见问题和解决步骤'
  },
  {
    id: 'monitoring',
    name: '监控策略',
    description: '监控指标和告警',
    icon: '📊',
    prompt: '帮我设计一套完整的系统监控策略，包括关键指标、告警阈值和处理流程'
  },
  {
    id: 'capacity',
    name: '容量规划',
    description: '资源容量评估',
    icon: '📈',
    prompt: '指导我进行系统容量规划，包括资源评估、扩容策略和成本优化'
  },
  {
    id: 'sla',
    name: 'SLA制定',
    description: '服务水平协议',
    icon: '📋',
    prompt: '帮我制定合理的SLA和SLO，包括可用性、性能和错误率等指标'
  },
  {
    id: 'automation',
    name: '自动化工具',
    description: '运维自动化建议',
    icon: '🤖',
    prompt: '推荐适合的运维自动化工具和实践，提高运维效率'
  },
  {
    id: 'architecture',
    name: '架构优化',
    description: '高可用架构设计',
    icon: '🏗️',
    prompt: '分析当前架构并提供高可用、高性能的优化建议'
  }
])

// 方法

// 渲染Markdown
const renderMarkdown = (text) => {
  if (!text) return ''
  try {
    return marked(text)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return text // fallback to plain text
  }
}

// 处理输入框回车键
const handleKeyDown = (event) => {
  if (event.key === 'Enter') {
    if (isComposing.value) {
      // 输入法组合中，不处理
      return
    }
    
    if (event.shiftKey) {
      // Shift+Enter 换行，不发送
      return
    }
    
    // 普通Enter键，发送消息
    event.preventDefault()
    sendMessage()
  }
}

const refreshSystemStatus = async () => {
  try {
    // 模拟系统状态检查
    systemStatus.value = { 
      healthy: Math.random() > 0.3,
      cpu: Math.floor(Math.random() * 40) + 40,
      memory: Math.floor(Math.random() * 30) + 60,
      availability: 99.9
    }
  } catch (error) {
    console.error('获取系统状态失败:', error)
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
  
  await generateSREResponse(userMessage)
}

const sendQuickPrompt = async (prompt) => {
  // 添加用户消息
  chatHistory.value.push({
    id: ++messageIdCounter,
    type: 'user',
    content: prompt
  })
  
  await generateSREResponse(prompt)
}

const generateSREResponse = async (prompt) => {
  aiThinking.value = true
  
  try {
    const response = await fetchApi('/simple-deploy/ai/sre', {
      method: 'POST',
      body: { prompt }
    })
    
    if (response.success) {
      chatHistory.value.push({
        id: ++messageIdCounter,
        type: 'ai',
        content: response.content,
        suggestions: response.suggestions || [],
        source: response.source || 'ai'
      })
    } else {
      chatHistory.value.push({
        id: ++messageIdCounter,
        type: 'ai',
        content: `抱歉，SRE助手响应失败: ${response.message}`
      })
    }
  } catch (error) {
    chatHistory.value.push({
      id: ++messageIdCounter,
      type: 'ai',
      content: `抱歉，SRE助手暂时不可用: ${error.message}`
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

const generateMockSREResponse = (prompt) => {
  // 根据关键词生成不同的响应
  if (prompt.includes('延迟') || prompt.includes('故障')) {
    return {
      content: '针对系统高延迟问题，我建议从以下几个维度进行排查和优化：',
      suggestions: [
        '检查服务器资源使用情况（CPU、内存、磁盘I/O）',
        '分析网络延迟和带宽使用情况',
        '查看数据库查询性能和慢查询日志',
        '检查缓存命中率和缓存策略',
        '分析应用程序性能瓶颈',
        '查看负载均衡器配置和后端服务状态'
      ]
    }
  } else if (prompt.includes('监控') || prompt.includes('告警')) {
    return {
      content: '完善的监控体系是SRE工作的基础，以下是建议的监控策略：',
      suggestions: [
        '建立四个黄金信号监控：延迟、流量、错误、饱和度',
        '设置合理的告警阈值，避免告警疲劳',
        '实施分级告警机制：P0紧急、P1重要、P2一般',
        '配置多维度监控：基础设施、应用、业务指标',
        '建立监控数据看板，提供可视化展示',
        '定期回顾和优化监控策略'
      ]
    }
  } else if (prompt.includes('性能') || prompt.includes('优化')) {
    return {
      content: '系统性能优化需要从多个层面入手，以下是系统性的优化方法：',
      suggestions: [
        '数据库层面：索引优化、查询优化、连接池调优',
        '应用层面：代码优化、缓存策略、异步处理',
        '架构层面：负载均衡、微服务拆分、CDN使用',
        '基础设施：服务器配置优化、网络优化',
        '监控调优：建立性能基线，持续监控关键指标',
        '容量规划：预测增长，提前扩容'
      ]
    }
  } else if (prompt.includes('灾难') || prompt.includes('恢复')) {
    return {
      content: '灾难恢复计划是确保业务连续性的重要保障，建议包含以下要素：',
      suggestions: [
        'RTO/RPO目标设定：恢复时间和数据丢失容忍度',
        '备份策略：定期备份、异地存储、备份验证',
        '故障演练：定期进行灾难恢复演练',
        '应急响应流程：明确责任人和处理步骤',
        '监控和告警：实时监控关键服务状态',
        '文档维护：保持恢复流程文档最新'
      ]
    }
  } else {
    return {
      content: '作为您的SRE助手，我建议采用系统性的方法来解决这个问题。让我为您提供一些通用的最佳实践：',
      suggestions: [
        '明确问题定义和影响范围',
        '收集相关监控数据和日志',
        '分析根本原因，避免治标不治本',
        '制定短期和长期解决方案',
        '建立预防措施，避免问题重复发生',
        '总结经验教训，更新操作手册'
      ]
    }
  }
}

const clearChat = () => {
  if (confirm('确定要清除所有对话记录吗？')) {
    chatHistory.value = []
    messageIdCounter = 0
  }
}

const exportChatHistory = () => {
  const content = chatHistory.value.map(msg => 
    `${msg.type === 'user' ? '问' : '答'}: ${msg.content}`
  ).join('\n\n')
  
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `sre-consultation-${new Date().getTime()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

// 组件挂载
onMounted(() => {
  refreshSystemStatus()
})
</script>

<style scoped>
.sre-scenario-btn {
  @apply p-4 border-2 border-dashed rounded-xl transition-all duration-200 text-center;
}

/* 聊天滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}

/* 渐变动画 */
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.bg-gradient-to-br {
  background-size: 200% 200%;
  animation: gradient 15s ease infinite;
}

/* Markdown 样式 */
.markdown-content {
  line-height: 1.6;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  font-weight: bold;
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #1f2937;
}

.markdown-content h1 { font-size: 1.5em; }
.markdown-content h2 { font-size: 1.3em; }
.markdown-content h3 { font-size: 1.1em; }

.markdown-content p {
  margin-bottom: 1em;
}

.markdown-content ul,
.markdown-content ol {
  margin-left: 1.5em;
  margin-bottom: 1em;
}

.markdown-content li {
  margin-bottom: 0.25em;
}

.markdown-content code {
  background-color: #f3f4f6;
  padding: 0.125em 0.25em;
  border-radius: 0.25em;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.875em;
  color: #dc2626;
}

.markdown-content pre {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 1em 0;
}

.markdown-content pre code {
  background: none;
  padding: 0;
  color: inherit;
}

.markdown-content blockquote {
  border-left: 4px solid #e5e7eb;
  padding-left: 1em;
  margin: 1em 0;
  font-style: italic;
  color: #6b7280;
}

.markdown-content strong {
  font-weight: bold;
}

.markdown-content em {
  font-style: italic;
}

.markdown-content a {
  color: #3b82f6;
  text-decoration: underline;
}

.markdown-content a:hover {
  color: #1d4ed8;
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 2em 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #e5e7eb;
  padding: 0.5em;
  text-align: left;
}

.markdown-content th {
  background-color: #f9fafb;
  font-weight: bold;
}
</style>