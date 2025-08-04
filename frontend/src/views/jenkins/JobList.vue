<template>
  <div class="space-y-6">
    <!-- 任务统计卡片 -->
    <JenkinsStatusCards
      v-if="selectedInstance"
      :stats="statusSummary"
      :loading="statusLoading"
      :show-extended="true"
      :show-trends="true"
      :auto-refresh="autoRefresh"
      @refresh="refreshData"
      @card-click="handleCardClick"
    />

    <!-- 任务列表区域 -->
    <div class="bg-white shadow rounded-lg">
      <!-- 列表头部 -->
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
          <div class="flex items-center space-x-4">
            <h2 class="text-xl font-semibold text-gray-900">🗂️ 任务列表</h2>
            <div v-if="selectedJobs.length > 0" class="flex items-center space-x-3 bg-blue-50 px-3 py-1 rounded-full">
              <span class="text-sm font-medium text-blue-700">已选择 {{ selectedJobs.length }} 个任务</span>
              <button 
                @click="batchBuild"
                :disabled="isLoading"
                class="inline-flex items-center px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                🚀 批量构建
              </button>
              <button 
                @click="clearSelection"
                class="inline-flex items-center px-2 py-1 bg-gray-500 text-white text-xs font-medium rounded hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                清除
              </button>
            </div>
          </div>
          
          <!-- 搜索和筛选 -->
          <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <input 
                type="text"
                v-model="searchQuery"
                placeholder="🔍 搜索任务..."
                class="block w-full sm:w-64 pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
            </div>
            
            <select 
              v-model="statusFilter"
              class="block w-full sm:w-32 px-3 py-2 border border-gray-300 bg-white rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">🏷️ 全部状态</option>
              <option value="success">✅ 成功</option>
              <option value="failure">❌ 失败</option>
              <option value="building">🟡 构建中</option>
              <option value="unknown">❓ 未知</option>
            </select>
            
            <select 
              v-model="viewMode"
              class="block w-full sm:w-28 px-3 py-2 border border-gray-300 bg-white rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="table">👁️ 表格</option>
              <option value="card">📋 卡片</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后构建</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">持续时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="job in filteredJobs" :key="job.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  :value="job.name"
                  v-model="selectedJobs"
                  class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                >
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <component 
                      :is="getJobIcon(job.type)"
                      class="h-5 w-5 text-gray-500"
                    />
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ job.name }}</div>
                    <div class="text-sm text-gray-500">{{ job.description }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">#{{ job.lastBuildNumber }}</div>
                <div class="text-sm text-gray-500">{{ job.lastBuildTime }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  getStatusClass(job.status)
                ]">
                  {{ getStatusText(job.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ job.duration }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                <button 
                  @click="triggerBuild(job)"
                  :disabled="isLoading"
                  class="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  构建
                </button>
                <button 
                  @click="viewLogs(job)"
                  class="text-purple-600 hover:text-purple-900"
                >
                  日志
                </button>
                <button 
                  @click="viewDetails(job)"
                  class="text-green-600 hover:text-green-900"
                >
                  详情
                </button>
                <button 
                  @click="editJob(job)"
                  class="text-gray-600 hover:text-gray-900"
                >
                  编辑
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 卡片视图 -->
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="job in filteredJobs" :key="job.id" 
               class="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  :value="job.name"
                  v-model="selectedJobs"
                  class="rounded border-gray-300 text-blue-600 shadow-sm"
                >
                <h3 class="font-medium text-gray-900">{{ job.name }}</h3>
              </div>
              <span :class="[
                'px-2 py-1 text-xs font-medium rounded-full',
                getStatusClass(job.status)
              ]">
                {{ getStatusText(job.status) }}
              </span>
            </div>
            
            <p class="text-sm text-gray-600 mb-3">{{ job.description }}</p>
            
            <div class="text-xs text-gray-500 mb-3">
              <div>最后构建: #{{ job.lastBuildNumber }}</div>
              <div>时间: {{ job.lastBuildTime }}</div>
              <div>耗时: {{ job.duration }}</div>
            </div>
            
            <div class="flex space-x-2">
              <button 
                @click="triggerBuild(job)"
                :disabled="isLoading"
                class="flex-1 bg-blue-500 text-white text-xs py-1 px-2 rounded hover:bg-blue-600 disabled:opacity-50"
              >
                构建
              </button>
              <button 
                @click="viewLogs(job)"
                class="flex-1 bg-purple-500 text-white text-xs py-1 px-2 rounded hover:bg-purple-600"
              >
                日志
              </button>
              <button 
                @click="editJob(job)"
                class="flex-1 bg-gray-500 text-white text-xs py-1 px-2 rounded hover:bg-gray-600"
              >
                编辑
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="filteredJobs.length === 0 && !isLoading" class="text-center py-12">
        <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m8-8v2m0 6h.01"/>
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">暂无任务</h3>
        <p class="text-gray-500 mb-4">当前实例中没有找到任务，或者任务被筛选条件过滤</p>
        <router-link 
          :to="{ name: 'jenkins-create' }"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          ➕ 创建新任务
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { 
  FolderIcon, 
  DocumentTextIcon,
  CogIcon
} from '@heroicons/vue/24/outline'
import JenkinsStatusCards from '@/components/jenkins/JenkinsStatusCards.vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

const router = useRouter()

// 注入全局状态
const selectedInstance = inject('jenkinsInstance')
const autoRefresh = inject('autoRefresh')

// 本地状态
const jobs = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const selectedJobs = ref([])
const viewMode = ref('table')
const isLoading = ref(false)
const statusLoading = ref(false)

// 状态统计
const statusSummary = ref({
  totalJobs: 0,
  buildingJobs: 0,
  queueCount: 0,
  successRate: 0,
  failedJobs: 0,
  successJobs: 0,
  averageDuration: 0,
  todayBuilds: 0
})

// 计算属性
const filteredJobs = computed(() => {
  return jobs.value.filter(job => {
    const matchesSearch = job.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !statusFilter.value || job.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

const isAllSelected = computed(() => {
  return filteredJobs.value.length > 0 && selectedJobs.value.length === filteredJobs.value.length
})

// 方法
const getJobIcon = (type) => {
  switch (type) {
    case 'pipeline': return DocumentTextIcon
    case 'freestyle': return FolderIcon  
    default: return CogIcon
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'success': return 'bg-green-100 text-green-800'
    case 'failure': return 'bg-red-100 text-red-800'
    case 'building': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'success': return '成功'
    case 'failure': return '失败'
    case 'building': return '构建中'
    default: return '未知'
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedJobs.value = []
  } else {
    selectedJobs.value = filteredJobs.value.map(job => job.name)
  }
}

const clearSelection = () => {
  selectedJobs.value = []
}

const triggerBuild = async (job) => {
  if (!selectedInstance.value) {
    notify.warning('请先选择Jenkins实例')
    return
  }
  
  isLoading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${job.name}`, {
      method: 'POST'
    })
    
    if (response.success) {
      notify.success(`任务 ${job.name} 构建已触发`)
      await refreshData()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('触发构建失败:', error)
    notify.error(`触发构建失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const batchBuild = async () => {
  if (selectedJobs.value.length === 0) {
    notify.warning('请先选择任务')
    return
  }
  
  if (!(await notify.confirm(`确定要批量构建选中的 ${selectedJobs.value.length} 个任务吗？`))) {
    return
  }
  
  isLoading.value = true
  try {
    const promises = selectedJobs.value.map(jobName => 
      fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${jobName}`, {
        method: 'POST'
      })
    )
    
    const results = await Promise.allSettled(promises)
    const successCount = results.filter(r => r.status === 'fulfilled' && r.value.success).length
    const failureCount = results.length - successCount
    
    if (failureCount > 0) {
      notify.warning(`批量构建完成: 成功 ${successCount} 个，失败 ${failureCount} 个`)
    } else {
      notify.success(`批量构建完成: 成功触发 ${successCount} 个任务`)
    }
    
    clearSelection()
    await refreshData()
  } catch (error) {
    console.error('批量构建失败:', error)
    notify.error(`批量构建失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const viewLogs = (job) => {
  // 跳转到构建监控页面查看日志
  router.push({ 
    name: 'jenkins-monitor', 
    query: { job: job.name, build: job.lastBuildNumber } 
  })
}

const viewDetails = (job) => {
  notify.info(`
    <div class="text-left">
      <h3 class="text-lg font-semibold mb-3">任务详情: ${job.name}</h3>
      <div class="space-y-2 text-sm">
        <div><strong>描述:</strong> ${job.description || '无描述'}</div>
        <div><strong>状态:</strong> ${getStatusText(job.status)}</div>
        <div><strong>最后构建:</strong> #${job.lastBuildNumber || '无构建记录'}</div>
        <div><strong>构建时间:</strong> ${job.lastBuildTime || '-'}</div>
        <div><strong>持续时间:</strong> ${job.duration || '-'}</div>
        <div><strong>类型:</strong> ${job.type}</div>
      </div>
    </div>
  `, { 
    title: '任务详情',
    timeout: 0
  })
}

const editJob = (job) => {
  // 跳转到创建任务页面进行编辑
  router.push({ 
    name: 'jenkins-create', 
    query: { edit: job.name } 
  })
}

const handleCardClick = (cardData) => {
  console.log('状态卡片被点击:', cardData)
}

const fetchJobs = async () => {
  if (!selectedInstance.value) return
  
  isLoading.value = true
  try {
    const response = await fetchApi(`/ops/jenkins/jobs/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      jobs.value = response.data.map(job => ({
        ...job,
        id: job.name,
        description: job.description || `Jenkins任务: ${job.name}`,
        type: job.buildable ? 'freestyle' : 'disabled',
        lastBuildTime: job.lastBuildTime ? new Date(job.lastBuildTime).toLocaleString() : '-',
        duration: job.duration ? `${Math.round(job.duration / 1000)}秒` : '-',
        lastBuildNumber: job.lastBuildNumber || 0
      }))
      
      calculateStatusSummary()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取Jenkins任务失败:', error)
    notify.error(`获取任务列表失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const calculateStatusSummary = () => {
  const total = jobs.value.length
  let building = 0, success = 0, failed = 0
  
  jobs.value.forEach(job => {
    switch (job.status) {
      case 'building': building++; break
      case 'success': success++; break
      case 'failure': failed++; break
    }
  })
  
  statusSummary.value = {
    totalJobs: total,
    buildingJobs: building,
    successJobs: success,
    failedJobs: failed,
    successRate: total > 0 ? Math.round((success / total) * 100) : 0,
    queueCount: 0, // 将从其他API获取
    averageDuration: 0, // 将计算平均耗时
    todayBuilds: 0 // 将从构建历史计算
  }
}

const refreshData = async () => {
  await fetchJobs()
}

// 监听实例变化
watch(selectedInstance, (newInstance) => {
  if (newInstance) {
    refreshData()
  } else {
    jobs.value = []
    statusSummary.value = {
      totalJobs: 0,
      buildingJobs: 0,
      queueCount: 0,
      successRate: 0,
      failedJobs: 0,
      successJobs: 0,
      averageDuration: 0,
      todayBuilds: 0
    }
  }
}, { immediate: true })

// 监听全局刷新事件
onMounted(() => {
  window.addEventListener('jenkins-refresh', refreshData)
})

onBeforeUnmount(() => {
  window.removeEventListener('jenkins-refresh', refreshData)
})
</script>

<style scoped>
/* 表格行悬停效果 */
.hover\:bg-gray-50:hover {
  transition: background-color 0.15s ease-in-out;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .grid {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>