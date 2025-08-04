<template>
  <div class="space-y-6">
    <!-- 构建状态概览 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              🚀
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">正在构建</div>
            <div class="text-2xl font-bold text-gray-900">{{ buildingCount }}</div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              ⏳
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">队列等待</div>
            <div class="text-2xl font-bold text-gray-900">{{ queueCount }}</div>
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
            <div class="text-sm font-medium text-gray-500">今日成功</div>
            <div class="text-2xl font-bold text-gray-900">{{ todaySuccessCount }}</div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
              ❌
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">今日失败</div>
            <div class="text-2xl font-bold text-gray-900">{{ todayFailureCount }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时构建和队列监控 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 正在构建的任务 -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">🚀 正在构建</h2>
            <button 
              @click="refreshBuilding"
              :disabled="isLoading"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              刷新
            </button>
          </div>
        </div>
        
        <div class="p-6">
          <div v-if="isLoading" class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"></div>
            <span class="text-gray-500">加载构建数据中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-8 text-gray-500">
            <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <p>请选择Jenkins实例查看构建状态</p>
          </div>
          <div v-else-if="runningBuilds.length === 0" class="text-center py-8 text-gray-500">
            <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            <p>当前没有正在构建的任务</p>
          </div>
          
          <div v-else class="space-y-4">
            <div 
              v-for="build in runningBuilds" 
              :key="build.id"
              class="border rounded-lg p-4 bg-gradient-to-r from-blue-50 to-indigo-50"
            >
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></div>
                  <h3 class="font-medium text-gray-900">{{ build.jobName }}</h3>
                  <span class="text-sm text-gray-500">#{{ build.number }}</span>
                </div>
                <div class="flex space-x-2">
                  <button 
                    @click="viewBuildLog(build)"
                    class="text-sm text-blue-600 hover:text-blue-800"
                  >
                    查看日志
                  </button>
                  <button 
                    @click="stopBuild(build)"
                    class="text-sm text-red-600 hover:text-red-800"
                  >
                    停止构建
                  </button>
                </div>
              </div>
              
              <div class="space-y-2">
                <div class="flex justify-between text-sm text-gray-600">
                  <span>进度</span>
                  <span>{{ build.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${build.progress}%` }"
                  ></div>
                </div>
                <div class="flex justify-between text-xs text-gray-500">
                  <span>开始时间: {{ build.startTime }}</span>
                  <span>已用时长: {{ build.duration }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 构建队列 -->
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-gray-900">⏳ 构建队列</h2>
            <button 
              @click="refreshQueue"
              :disabled="isLoading"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              刷新
            </button>
          </div>
        </div>
        
        <div class="p-6">
          <div v-if="isLoading" class="flex items-center justify-center py-8">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"></div>
            <span class="text-gray-500">加载队列数据中...</span>
          </div>
          <div v-else-if="!selectedInstance" class="text-center py-8 text-gray-500">
            <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
              </svg>
            </div>
            <p>请选择Jenkins实例查看队列状态</p>
          </div>
          <div v-else-if="buildQueue.length === 0" class="text-center py-8 text-gray-500">
            <div class="w-12 h-12 mx-auto mb-4 text-gray-400">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <p>当前队列为空</p>
          </div>
          
          <div v-else class="space-y-3">
            <div 
              v-for="(item, index) in buildQueue" 
              :key="item.id"
              class="border rounded-lg p-4 bg-gradient-to-r from-yellow-50 to-orange-50"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center space-x-3">
                  <span class="flex items-center justify-center w-6 h-6 bg-yellow-100 text-yellow-600 rounded-full text-xs font-medium">
                    {{ index + 1 }}
                  </span>
                  <h3 class="font-medium text-gray-900">{{ item.jobName }}</h3>
                </div>
                <div class="flex space-x-2">
                  <button 
                    @click="cancelQueueItem(item)"
                    class="text-sm text-red-600 hover:text-red-800"
                  >
                    取消
                  </button>
                </div>
              </div>
              
              <div class="text-sm text-gray-600 space-y-1">
                <div>触发原因: {{ item.why }}</div>
                <div>等待时长: {{ item.waitTime }}</div>
                <div v-if="item.blockedReason">阻塞原因: {{ item.blockedReason }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近构建历史 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">📈 最近构建历史</h2>
          <div class="flex items-center space-x-4">
            <select 
              v-model="historyFilter"
              class="text-sm rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">全部任务</option>
              <option v-for="job in availableJobs" :key="job" :value="job">{{ job }}</option>
            </select>
            
            <select 
              v-model="statusFilter"
              class="text-sm rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">全部状态</option>
              <option value="success">成功</option>
              <option value="failure">失败</option>
              <option value="aborted">已中止</option>
            </select>
            
            <button 
              @click="refreshHistory"
              :disabled="isLoading"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              刷新
            </button>
          </div>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">构建号</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">开始时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">耗时</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">触发者</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="build in filteredBuildHistory" :key="build.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="font-medium text-gray-900">{{ build.jobName }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">#{{ build.number }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  getBuildStatusClass(build.status)
                ]">
                  {{ getBuildStatusText(build.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ build.startTime }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ build.duration }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ build.triggeredBy }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                <button 
                  @click="viewBuildLog(build)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  日志
                </button>
                <button 
                  @click="viewBuildDetails(build)"
                  class="text-green-600 hover:text-green-900"
                >
                  详情
                </button>
                <button 
                  v-if="build.status !== 'building'"
                  @click="rebuildJob(build)"
                  class="text-purple-600 hover:text-purple-900"
                >
                  重新构建
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div v-if="totalBuilds > pageSize" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            显示 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, totalBuilds) }} 条，共 {{ totalBuilds }} 条
          </div>
          <div class="flex space-x-2">
            <button 
              @click="currentPage--"
              :disabled="currentPage <= 1"
              class="px-3 py-1 text-sm border rounded disabled:opacity-50"
            >
              上一页
            </button>
            <button 
              @click="currentPage++"
              :disabled="currentPage >= Math.ceil(totalBuilds / pageSize)"
              class="px-3 py-1 text-sm border rounded disabled:opacity-50"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 构建日志查看对话框 -->
    <TransitionRoot appear :show="showLogDialog" as="template">
      <Dialog as="div" @close="showLogDialog = false" class="relative z-10">
        <TransitionChild
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4">
            <TransitionChild
              enter="ease-out duration-300"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-6xl transform overflow-hidden rounded-2xl bg-white text-left align-middle shadow-xl transition-all">
                <div class="p-6">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                    构建日志 - {{ currentLogBuild?.jobName }} #{{ currentLogBuild?.number }}
                  </DialogTitle>

                  <!-- 日志工具栏 -->
                  <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-4">
                      <button 
                        @click="toggleAutoRefreshLog"
                        :disabled="isLoading"
                        class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600 disabled:opacity-50"
                      >
                        {{ autoRefreshLog ? '停止自动刷新' : '自动刷新' }}
                      </button>
                      <button 
                        @click="downloadBuildLog"
                        class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                      >
                        下载日志
                      </button>
                    </div>
                    <div class="flex items-center space-x-2">
                      <input 
                        type="text"
                        v-model="logSearchQuery"
                        placeholder="搜索日志..."
                        class="block w-64 text-sm rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      >
                    </div>
                  </div>

                  <!-- 日志内容 -->
                  <div class="bg-black text-green-400 p-4 rounded-lg h-96 overflow-y-auto font-mono text-sm">
                    <div v-if="isLoading" class="text-center text-gray-500 flex items-center justify-center h-full">
                      <div class="flex items-center space-x-2">
                        <svg class="animate-spin h-5 w-5 text-green-400" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>加载日志中...</span>
                      </div>
                    </div>
                    <div v-else-if="!logContent" class="text-center text-gray-500">
                      暂无日志内容
                    </div>
                    <pre v-else class="whitespace-pre-wrap">{{ filteredLogContent }}</pre>
                  </div>

                  <div class="mt-6 flex justify-end">
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                      @click="showLogDialog = false"
                    >
                      关闭
                    </button>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, inject, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

const route = useRoute()

// 注入全局状态
const selectedInstance = inject('jenkinsInstance')

// 响应式状态
const isLoading = ref(false)
const runningBuilds = ref([])
const buildQueue = ref([])
const buildHistory = ref([])
const availableJobs = ref([])

// 统计数据
const buildingCount = ref(0)
const queueCount = ref(0)
const todaySuccessCount = ref(0)
const todayFailureCount = ref(0)

// 筛选和分页
const historyFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalBuilds = ref(0)

// 日志相关
const showLogDialog = ref(false)
const currentLogBuild = ref(null)
const logContent = ref('')
const logSearchQuery = ref('')
const autoRefreshLog = ref(false)
let logRefreshInterval = null

// 计算属性
const filteredBuildHistory = computed(() => {
  return buildHistory.value.filter(build => {
    const matchesJob = !historyFilter.value || build.jobName === historyFilter.value
    const matchesStatus = !statusFilter.value || build.status === statusFilter.value
    return matchesJob && matchesStatus
  })
})

const filteredLogContent = computed(() => {
  if (!logContent.value) return ''
  
  if (logSearchQuery.value.trim()) {
    const query = logSearchQuery.value.toLowerCase()
    const lines = logContent.value.split('\n')
    return lines.filter(line => 
      line.toLowerCase().includes(query)
    ).join('\n')
  }
  
  return logContent.value
})

// 方法
const getBuildStatusClass = (status) => {
  switch (status) {
    case 'success': return 'bg-green-100 text-green-800'
    case 'failure': return 'bg-red-100 text-red-800'
    case 'building': return 'bg-blue-100 text-blue-800'
    case 'aborted': return 'bg-gray-100 text-gray-800'
    default: return 'bg-yellow-100 text-yellow-800'
  }
}

const getBuildStatusText = (status) => {
  switch (status) {
    case 'success': return '成功'
    case 'failure': return '失败'
    case 'building': return '构建中'
    case 'aborted': return '已中止'
    default: return '未知'
  }
}

const refreshBuilding = async () => {
  if (!selectedInstance.value) return
  
  isLoading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/builds/running/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      runningBuilds.value = response.data.map(build => ({
        ...build,
        startTime: new Date(build.startTime).toLocaleString(),
        duration: formatDuration(build.duration)
      }))
      buildingCount.value = runningBuilds.value.length
    }
  } catch (error) {
    console.error('获取正在构建的任务失败:', error)
    notify.error(`获取构建状态失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const refreshQueue = async () => {
  if (!selectedInstance.value) return
  
  try {
    const response = await fetchApi(`/ops/jenkins/queue/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      buildQueue.value = response.data.map(item => ({
        ...item,
        waitTime: formatDuration(item.inQueueSince)
      }))
      queueCount.value = buildQueue.value.length
    }
  } catch (error) {
    console.error('获取构建队列失败:', error)
    notify.error(`获取队列状态失败: ${error.message}`)
  }
}

const refreshHistory = async () => {
  if (!selectedInstance.value) return
  
  isLoading.value = true
  try {
    // Construct URL with query parameters
    const params = new URLSearchParams({
      page: currentPage.value.toString(),
      size: pageSize.value.toString(),
      ...(historyFilter.value && { job: historyFilter.value }),
      ...(statusFilter.value && { status: statusFilter.value })
    })
    
    const response = await fetchApi(`/ops/jenkins/builds/history/${selectedInstance.value}?${params}`, {
      method: 'GET'
    })
    
    if (response.success) {
      buildHistory.value = response.data.builds.map(build => ({
        ...build,
        startTime: new Date(build.startTime).toLocaleString(),
        duration: formatDuration(build.duration)
      }))
      totalBuilds.value = response.data.total
      
      // 更新可用任务列表
      availableJobs.value = [...new Set(buildHistory.value.map(build => build.jobName))]
      
      // 计算今日统计
      calculateTodayStats()
    }
  } catch (error) {
    console.error('获取构建历史失败:', error)
    notify.error(`获取构建历史失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const calculateTodayStats = () => {
  const today = new Date().toDateString()
  const todayBuilds = buildHistory.value.filter(build => 
    new Date(build.startTime).toDateString() === today
  )
  
  todaySuccessCount.value = todayBuilds.filter(build => build.status === 'success').length
  todayFailureCount.value = todayBuilds.filter(build => build.status === 'failure').length
}

const formatDuration = (ms) => {
  if (!ms) return '-'
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

const viewBuildLog = async (build) => {
  currentLogBuild.value = build
  showLogDialog.value = true
  await fetchBuildLog(build.jobName, build.number)
}

const fetchBuildLog = async (jobName, buildNumber) => {
  if (!selectedInstance.value) return
  
  logContent.value = ''
  isLoading.value = true
  
  try {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${jobName}/${buildNumber}/log`, {
      method: 'GET'
    })
    
    if (response.success) {
      logContent.value = response.data.log
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取构建日志失败:', error)
    logContent.value = `获取日志失败: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const toggleAutoRefreshLog = () => {
  autoRefreshLog.value = !autoRefreshLog.value
  
  if (autoRefreshLog.value && currentLogBuild.value) {
    logRefreshInterval = setInterval(() => {
      fetchBuildLog(currentLogBuild.value.jobName, currentLogBuild.value.number)
    }, 5000) // 每5秒刷新
  } else {
    if (logRefreshInterval) {
      clearInterval(logRefreshInterval)
      logRefreshInterval = null
    }
  }
}

const refreshBuildLog = async () => {
  if (currentLogBuild.value) {
    await fetchBuildLog(currentLogBuild.value.jobName, currentLogBuild.value.number)
  }
}

const downloadBuildLog = () => {
  if (!logContent.value || !currentLogBuild.value) return
  
  const blob = new Blob([logContent.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${currentLogBuild.value.jobName}-${currentLogBuild.value.number}.log`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

const stopBuild = async (build) => {
  if (!(await notify.confirm(`确定要停止构建 ${build.jobName} #${build.number} 吗？`))) {
    return
  }
  
  try {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${build.jobName}/${build.number}/stop`, {
      method: 'POST'
    })
    
    if (response.success) {
      notify.success('构建已停止')
      await refreshBuilding()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('停止构建失败:', error)
    notify.error(`停止构建失败: ${error.message}`)
  }
}

const cancelQueueItem = async (item) => {
  if (!(await notify.confirm(`确定要取消队列中的 ${item.jobName} 吗？`))) {
    return
  }
  
  try {
    const response = await fetchApi(`/ops/jenkins/queue/${selectedInstance.value}/${item.id}/cancel`, {
      method: 'POST'
    })
    
    if (response.success) {
      notify.success('队列项已取消')
      await refreshQueue()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('取消队列项失败:', error)
    notify.error(`取消失败: ${error.message}`)
  }
}

const rebuildJob = async (build) => {
  try {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${build.jobName}`, {
      method: 'POST'
    })
    
    if (response.success) {
      notify.success(`任务 ${build.jobName} 重新构建已触发`)
      await refreshBuilding()
      await refreshQueue()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('重新构建失败:', error)
    notify.error(`重新构建失败: ${error.message}`)
  }
}

const viewBuildDetails = (build) => {
  notify.info(`
    <div class="text-left">
      <h3 class="text-lg font-semibold mb-3">构建详情: ${build.jobName} #${build.number}</h3>
      <div class="space-y-2 text-sm">
        <div><strong>状态:</strong> ${getBuildStatusText(build.status)}</div>
        <div><strong>开始时间:</strong> ${build.startTime}</div>
        <div><strong>持续时间:</strong> ${build.duration}</div>
        <div><strong>触发者:</strong> ${build.triggeredBy}</div>
        <div><strong>构建原因:</strong> ${build.cause || '手动触发'}</div>
      </div>
    </div>
  `, { 
    title: '构建详情',
    timeout: 0
  })
}

const refreshAll = async () => {
  await Promise.all([
    refreshBuilding(),
    refreshQueue(),
    refreshHistory()
  ])
}

// 监听实例变化
watch(selectedInstance, async (newInstance) => {
  if (newInstance) {
    await refreshAll()
  } else {
    // 清空数据当实例为空时
    runningBuilds.value = []
    buildQueue.value = []
    buildHistory.value = []
    buildingCount.value = 0
    queueCount.value = 0
    todaySuccessCount.value = 0
    todayFailureCount.value = 0
  }
}, { immediate: true })

// 初始化和清理
onMounted(async () => {
  // 检查是否从任务列表跳转过来查看特定日志
  if (route.query.job && route.query.build) {
    const build = {
      jobName: route.query.job,
      number: route.query.build
    }
    await viewBuildLog(build)
  }
  
  // 监听全局刷新事件
  window.addEventListener('jenkins-refresh', refreshAll)
})

onBeforeUnmount(() => {
  if (logRefreshInterval) {
    clearInterval(logRefreshInterval)
  }
  window.removeEventListener('jenkins-refresh', refreshAll)
})
</script>

<style scoped>
/* 构建进度动画 */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: .5;
  }
}

/* 渐变背景 */
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}

/* 自定义滚动条 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* 表格行悬停效果 */
.hover\:bg-gray-50:hover {
  transition: background-color 0.15s ease-in-out;
}
</style>