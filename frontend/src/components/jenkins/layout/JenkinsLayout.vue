<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Jenkins页面标题栏 -->
    <div class="bg-white border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-6">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            🏗️ Jenkins管理
          </h1>
          
          <!-- Jenkins实例选择器 -->
          <div class="ml-8">
            <JenkinsInstanceSelector
              v-model="selectedInstance"
              @change="onInstanceChange"
              show-status
              show-stats
              class="max-w-lg"
            />
          </div>
        </div>
        
        <!-- 全局操作按钮 -->
        <div class="flex items-center space-x-3">
          <button 
            @click="refreshAll"
            :disabled="!selectedInstance || isRefreshing"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            <svg v-if="isRefreshing" class="animate-spin -ml-1 mr-1 h-4 w-4 text-gray-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            🔄 刷新
          </button>
          
          <button 
            @click="toggleAutoRefresh"
            :disabled="!selectedInstance"
            :class="[
              'inline-flex items-center px-3 py-2 border shadow-sm text-sm leading-4 font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50',
              autoRefresh 
                ? 'border-green-300 text-green-700 bg-green-50 hover:bg-green-100' 
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
            ]"
          >
            {{ autoRefresh ? '⚡ 自动刷新(开)' : '⚡ 自动刷新(关)' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Jenkins子导航 -->
    <div class="bg-white border-b border-gray-200">
      <nav class="flex space-x-8 px-6" aria-label="Jenkins Navigation">
        <template v-if="selectedInstance">
          <router-link
            v-for="navItem in navigationItems"
            :key="navItem.name"
            :to="{ name: navItem.name }"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
              $route.name === navItem.name
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ navItem.icon }} {{ navItem.label }}
          </router-link>
        </template>
        <template v-else>
          <div
            v-for="navItem in navigationItems"
            :key="navItem.name"
            :class="[
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm cursor-not-allowed',
              'border-transparent text-gray-300'
            ]"
            :title="'请先选择Jenkins实例'"
          >
            {{ navItem.icon }} {{ navItem.label }}
          </div>
        </template>
      </nav>
    </div>

    <!-- 内容区域 -->
    <main class="p-6">
      <!-- 空状态提示 -->
      <div v-if="!selectedInstance" class="text-center py-12">
        <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">选择Jenkins实例</h3>
        <p class="text-gray-500 mb-4">请先选择一个Jenkins实例来开始管理</p>
        <router-link 
          to="/settings/jenkins"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          ➕ 添加Jenkins实例
        </router-link>
      </div>
      
      <!-- 页面内容 -->
      <div v-else>
        <router-view 
          :selected-instance="selectedInstance"
          :auto-refresh="autoRefresh"
          @refresh="refreshAll"
        ></router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, provide } from 'vue'
import { useRoute } from 'vue-router'
import JenkinsInstanceSelector from '@/components/jenkins/JenkinsInstanceSelector.vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

const route = useRoute()

// 状态管理
const selectedInstance = ref('')
const autoRefresh = ref(false)
const isRefreshing = ref(false)
let refreshInterval = null

// Jenkins导航项
const navigationItems = [
  { name: 'jenkins-jobs', label: '任务列表', icon: '📋' },
  { name: 'jenkins-create', label: '创建任务', icon: '➕' },
  { name: 'jenkins-monitor', label: '构建监控', icon: '📊' },
  { name: 'jenkins-instances', label: '实例管理', icon: '🔧' },
  { name: 'jenkins-analytics', label: '分析报告', icon: '📈' }
]

// 刷新所有数据
const refreshAll = async () => {
  if (!selectedInstance.value) return
  
  isRefreshing.value = true
  try {
    // 触发全局刷新事件
    window.dispatchEvent(new CustomEvent('jenkins-refresh', {
      detail: { instance: selectedInstance.value }
    }))
    
    await new Promise(resolve => setTimeout(resolve, 1000)) // 最小显示时间
  } catch (error) {
    console.error('刷新失败:', error)
    notify.error('刷新失败')
  } finally {
    isRefreshing.value = false
  }
}

// 提供全局状态给子组件
provide('jenkinsInstance', selectedInstance)
provide('autoRefresh', autoRefresh)
provide('refreshTrigger', refreshAll)

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  
  if (autoRefresh.value && selectedInstance.value) {
    refreshInterval = setInterval(() => {
      refreshAll()
    }, 30000) // 30秒自动刷新
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
}

// 监听实例变化
const onInstanceChange = async (instanceId, instanceData) => {
  console.log('Jenkins实例已切换:', instanceId, instanceData)
  
  // 重置自动刷新
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
  
  if (autoRefresh.value && instanceId) {
    refreshInterval = setInterval(() => {
      refreshAll()
    }, 30000)
  }
  
  // 触发数据刷新
  if (instanceId) {
    await refreshAll()
  }
}

// 组件卸载时清理
onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
/* 子导航高亮效果 */
.router-link-exact-active {
  @apply border-blue-500 text-blue-600;
}

/* 导航项悬停效果 */
nav a:hover {
  @apply text-gray-700 border-gray-300;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .flex.items-center.justify-between {
    @apply flex-col items-start space-y-4;
  }
  
  nav {
    @apply overflow-x-auto;
  }
  
  nav a {
    @apply whitespace-nowrap;
  }
}
</style>