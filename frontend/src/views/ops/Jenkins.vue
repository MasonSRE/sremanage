<template>
  <div class="space-y-6">
    <!-- Jenkins实例选择器 -->
    <div class="bg-white rounded-lg shadow p-6">
      <div class="flex items-center space-x-4">
        <label class="text-sm font-medium text-gray-700">Jenkins实例:</label>
        <select 
          v-model="selectedInstance"
          @change="onInstanceChange"
          class="mt-1 block w-64 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option v-for="instance in jenkinsInstances" :key="instance.id" :value="instance.id">
            {{ instance.name }}
          </option>
        </select>
        <button 
          class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
          @click="addNewInstance"
        >
          添加Jenkins实例
        </button>
      </div>
    </div>

    <!-- Jenkins任务列表 -->
    <div class="bg-white rounded-lg shadow">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">任务列表</h2>
          <div class="flex space-x-4">
            <div class="relative">
              <input 
                type="text"
                v-model="searchQuery"
                placeholder="搜索任务..."
                class="block w-64 rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
            </div>
            <select 
              v-model="statusFilter"
              class="block w-32 rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">全部状态</option>
              <option value="success">成功</option>
              <option value="failure">失败</option>
              <option value="building">构建中</option>
            </select>
          </div>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">任务名称</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后构建</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">持续时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="job in filteredJobs" :key="job.id">
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
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button 
                  @click="triggerBuild(job)"
                  class="text-blue-600 hover:text-blue-900 mr-3"
                >
                  构建
                </button>
                <button 
                  @click="viewDetails(job)"
                  class="text-green-600 hover:text-green-900 mr-3"
                >
                  详情
                </button>
                <button 
                  @click="showConfig(job)"
                  class="text-gray-600 hover:text-gray-900"
                >
                  配置
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 构建历史 -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">构建历史</h2>
      <div class="space-y-4">
        <div v-for="build in buildHistory" :key="build.id" 
             class="border rounded-lg p-4 hover:bg-gray-50">
          <div class="flex justify-between items-center">
            <div>
              <span class="font-medium">{{ build.jobName }}</span>
              <span class="text-gray-500 ml-2">#{{ build.number }}</span>
            </div>
            <span :class="[
              'px-2 py-1 text-xs font-semibold rounded-full',
              getStatusClass(build.status)
            ]">
              {{ getStatusText(build.status) }}
            </span>
          </div>
          <div class="mt-2 text-sm text-gray-500">
            <span>触发者: {{ build.triggeredBy }}</span>
            <span class="mx-2">|</span>
            <span>开始时间: {{ build.startTime }}</span>
            <span class="mx-2">|</span>
            <span>持续时间: {{ build.duration }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 添加Jenkins实例对话框 -->
  <TransitionRoot appear :show="showAddDialog" as="template">
    <Dialog as="div" @close="showAddDialog = false" class="relative z-10">
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
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                添加Jenkins实例
              </DialogTitle>

              <div class="mt-4 space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">实例名称</label>
                  <input 
                    type="text"
                    v-model="newInstance.name"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Jenkins URL</label>
                  <input 
                    type="text"
                    v-model="newInstance.url"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">用户名</label>
                  <input 
                    type="text"
                    v-model="newInstance.username"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">API Token</label>
                  <input 
                    type="password"
                    v-model="newInstance.token"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                </div>
              </div>

              <div class="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  @click="showAddDialog = false"
                >
                  取消
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  @click="saveNewInstance"
                >
                  保存
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { 
  FolderIcon, 
  PlayIcon, 
  CogIcon,
  DocumentTextIcon 
} from '@heroicons/vue/24/outline'
import { fetchApi } from '@/utils/api'

// 状态管理
const selectedInstance = ref('')
const searchQuery = ref('')
const statusFilter = ref('')
const showAddDialog = ref(false)
const newInstance = ref({
  name: '',
  url: '',
  username: '',
  token: ''
})

// Jenkins实例数据
const jenkinsInstances = ref([])

const jobs = ref([
  {
    id: 1,
    name: 'frontend-build',
    description: '前端构建任务',
    type: 'freestyle',
    lastBuildNumber: 123,
    lastBuildTime: '2024-01-20 15:30:00',
    status: 'success',
    duration: '2分钟'
  },
  {
    id: 2,
    name: 'backend-deploy',
    description: '后端部署任务',
    type: 'pipeline',
    lastBuildNumber: 45,
    lastBuildTime: '2024-01-20 14:20:00',
    status: 'failure',
    duration: '5分钟'
  }
])

const buildHistory = ref([
  {
    id: 1,
    jobName: 'frontend-build',
    number: 123,
    status: 'success',
    triggeredBy: 'admin',
    startTime: '2024-01-20 15:30:00',
    duration: '2分钟'
  },
  {
    id: 2,
    jobName: 'backend-deploy',
    number: 45,
    status: 'failure',
    triggeredBy: 'system',
    startTime: '2024-01-20 14:20:00',
    duration: '5分钟'
  }
])

// 计算属性
const filteredJobs = computed(() => {
  return jobs.value.filter(job => {
    const matchesSearch = job.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         job.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !statusFilter.value || job.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})

// 方法
const getJobIcon = (type) => {
  switch (type) {
    case 'pipeline':
      return DocumentTextIcon
    case 'freestyle':
      return FolderIcon
    default:
      return CogIcon
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'success':
      return 'bg-green-100 text-green-800'
    case 'failure':
      return 'bg-red-100 text-red-800'
    case 'building':
      return 'bg-yellow-100 text-yellow-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'success':
      return '成功'
    case 'failure':
      return '失败'
    case 'building':
      return '构建中'
    default:
      return '未知'
  }
}

const addNewInstance = () => {
  showAddDialog.value = true
}

const saveNewInstance = async () => {
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'POST',
      body: newInstance.value
    })
    
    if (response.success) {
      alert('Jenkins实例添加成功')
      showAddDialog.value = false
      newInstance.value = { name: '', url: '', username: '', token: '' }
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存Jenkins实例失败:', error)
    alert(error.message || '保存失败')
  }
}

const triggerBuild = async (job) => {
  if (!selectedInstance.value) {
    alert('请先选择Jenkins实例')
    return
  }
  
  try {
    const response = await fetchApi(`/ops/jenkins/build/${selectedInstance.value}/${job.name}`, {
      method: 'POST'
    })
    
    if (response.success) {
      alert(response.message)
      // 刷新任务列表
      await fetchJobs()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('触发构建失败:', error)
    alert(error.message || '触发构建失败')
  }
}

const viewDetails = (job) => {
  console.log('查看详情:', job.name)
  // TODO: 实现查看详情逻辑
}

const showConfig = (job) => {
  console.log('查看配置:', job.name)
  // TODO: 实现查看配置逻辑
}

// 获取Jenkins实例列表
const fetchInstances = async () => {
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'GET'
    })
    
    if (response.success) {
      jenkinsInstances.value = response.data
      if (jenkinsInstances.value.length > 0 && !selectedInstance.value) {
        selectedInstance.value = jenkinsInstances.value[0].id
        await fetchJobs()
      }
    }
  } catch (error) {
    console.error('获取Jenkins实例失败:', error)
  }
}

// 获取Jenkins任务列表
const fetchJobs = async () => {
  if (!selectedInstance.value) return
  
  try {
    const response = await fetchApi(`/ops/jenkins/jobs/${selectedInstance.value}`, {
      method: 'GET'
    })
    
    if (response.success) {
      jobs.value = response.data.map(job => ({
        ...job,
        id: job.name,
        description: `Jenkins任务: ${job.name}`,
        type: 'freestyle',
        lastBuildTime: job.lastBuildTime ? new Date(job.lastBuildTime).toLocaleString() : '-',
        duration: job.duration ? `${Math.round(job.duration / 1000)}秒` : '-'
      }))
    } else {
      console.error('获取Jenkins任务失败:', response.message)
    }
  } catch (error) {
    console.error('获取Jenkins任务失败:', error)
  }
}

// 监听实例选择变化
const onInstanceChange = async () => {
  await fetchJobs()
}

// 组件挂载时获取数据
onMounted(() => {
  fetchInstances()
})
</script>

<script>
export default {
  name: 'Jenkins'
}
</script>