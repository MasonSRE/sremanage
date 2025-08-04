<template>
  <div class="space-y-6">
    <!-- 页面标题和操作 -->
    <div class="bg-white rounded-lg shadow-sm border p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">🔧 Jenkins实例管理</h1>
          <p class="mt-1 text-sm text-gray-600">
            管理Jenkins服务器实例的连接配置和监控状态
          </p>
        </div>
        <button 
          @click="showAddDialog = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          ➕ 添加实例
        </button>
      </div>
    </div>

    <!-- 实例统计概览 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              🏗️
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">总实例数</div>
            <div class="text-2xl font-bold text-gray-900">{{ instances.length }}</div>
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
            <div class="text-sm font-medium text-gray-500">在线实例</div>
            <div class="text-2xl font-bold text-gray-900">{{ onlineInstances.length }}</div>
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
            <div class="text-sm font-medium text-gray-500">离线实例</div>
            <div class="text-2xl font-bold text-gray-900">{{ offlineInstances.length }}</div>
          </div>
        </div>
      </div>
      
      <div class="bg-white rounded-lg shadow-sm border p-4">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
              ⚠️
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-500">禁用实例</div>
            <div class="text-2xl font-bold text-gray-900">{{ disabledInstances.length }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实例列表 -->
    <div class="bg-white rounded-lg shadow-sm border">
      <div class="px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900">实例列表</h2>
          <div class="flex items-center space-x-4">
            <div class="relative">
              <input 
                type="text"
                v-model="searchQuery"
                placeholder="搜索实例..."
                class="block w-64 text-sm rounded-md border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
            </div>
            <select 
              v-model="statusFilter"
              class="text-sm rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="">全部状态</option>
              <option value="online">在线</option>
              <option value="offline">离线</option>
              <option value="disabled">禁用</option>
            </select>
            <button 
              @click="refreshAllInstances"
              :disabled="isLoading"
              class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
            >
              刷新全部
            </button>
          </div>
        </div>
      </div>
      
      <div class="divide-y divide-gray-200">
        <div v-if="filteredInstances.length === 0" class="text-center py-12">
          <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
          </div>
          <h3 class="text-lg font-medium text-gray-900 mb-2">暂无Jenkins实例</h3>
          <p class="text-gray-500 mb-4">开始添加您的首个Jenkins实例</p>
          <button 
            @click="showAddDialog = true"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            ➕ 添加首个实例
          </button>
        </div>
        
        <div 
          v-for="instance in filteredInstances" 
          :key="instance.id"
          class="p-6 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- 状态指示器 -->
              <div class="flex-shrink-0">
                <div :class="[
                  'w-3 h-3 rounded-full',
                  instance.status === 'online' ? 'bg-green-400' :
                  instance.status === 'offline' ? 'bg-red-400' :
                  instance.status === 'testing' ? 'bg-yellow-400 animate-pulse' :
                  'bg-gray-400'
                ]"></div>
              </div>
              
              <!-- 实例信息 -->
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="text-lg font-medium text-gray-900">{{ instance.name }}</h3>
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full font-medium',
                    instance.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  ]">
                    {{ instance.enabled ? '启用' : '禁用' }}
                  </span>
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full font-medium',
                    getStatusClass(instance.status)
                  ]">
                    {{ getStatusText(instance.status) }}
                  </span>
                </div>
                
                <div class="mt-1 space-y-1">
                  <p class="text-sm text-gray-600">{{ instance.url }}</p>
                  <div class="flex items-center space-x-4 text-xs text-gray-500">
                    <span>用户: {{ instance.username }}</span>
                    <span>版本: {{ instance.version || '未知' }}</span>
                    <span>最后检查: {{ instance.lastChecked || '从未' }}</span>
                  </div>
                </div>
              </div>
              
              <!-- 快速信息 -->
              <div v-if="instance.status === 'online' && instance.stats" class="text-right">
                <div class="text-sm text-gray-900">{{ instance.stats.totalJobs || 0 }} 任务</div>
                <div class="text-xs text-gray-500">{{ instance.stats.queueSize || 0 }} 队列</div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="flex items-center space-x-2">
              <button 
                @click="testConnection(instance)"
                :disabled="isLoading || instance.status === 'testing'"
                class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
              >
                {{ instance.status === 'testing' ? '测试中...' : '测试连接' }}
              </button>
              <button 
                @click="viewInstanceDetails(instance)"
                class="text-sm text-green-600 hover:text-green-800"
              >
                详情
              </button>
              <button 
                @click="editInstance(instance)"
                class="text-sm text-yellow-600 hover:text-yellow-800"
              >
                编辑
              </button>
              <button 
                @click="toggleInstance(instance)"
                :class="[
                  'text-sm hover:opacity-80',
                  instance.enabled ? 'text-orange-600' : 'text-green-600'
                ]"
              >
                {{ instance.enabled ? '禁用' : '启用' }}
              </button>
              <button 
                @click="deleteInstance(instance)"
                class="text-sm text-red-600 hover:text-red-800"
              >
                删除
              </button>
            </div>
          </div>
          
          <!-- 展开的详细信息 -->
          <div v-if="instance.showDetails" class="mt-4 p-4 bg-gray-50 rounded-lg">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">连接信息</h4>
                <dl class="text-xs space-y-1">
                  <div class="flex justify-between">
                    <dt class="text-gray-500">URL:</dt>
                    <dd class="text-gray-900">{{ instance.url }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500">用户名:</dt>
                    <dd class="text-gray-900">{{ instance.username }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500">创建时间:</dt>
                    <dd class="text-gray-900">{{ formatDate(instance.createdAt) }}</dd>
                  </div>
                </dl>
              </div>
              
              <div v-if="instance.stats">
                <h4 class="text-sm font-medium text-gray-900 mb-2">统计信息</h4>
                <dl class="text-xs space-y-1">
                  <div class="flex justify-between">
                    <dt class="text-gray-500">总任务数:</dt>
                    <dd class="text-gray-900">{{ instance.stats.totalJobs || 0 }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500">队列大小:</dt>
                    <dd class="text-gray-900">{{ instance.stats.queueSize || 0 }}</dd>
                  </div>
                  <div class="flex justify-between">
                    <dt class="text-gray-500">执行器数:</dt>
                    <dd class="text-gray-900">{{ instance.stats.executors || 0 }}</dd>
                  </div>
                </dl>
              </div>
              
              <div>
                <h4 class="text-sm font-medium text-gray-900 mb-2">健康状态</h4>
                <div class="space-y-2">
                  <div v-if="instance.healthCheck" class="space-y-1">
                    <div v-for="(status, check) in instance.healthCheck" :key="check" 
                         class="flex items-center justify-between">
                      <span class="text-xs text-gray-500">{{ check }}:</span>
                      <span :class="[
                        'text-xs px-1 py-0.5 rounded',
                        status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      ]">
                        {{ status ? '正常' : '异常' }}
                      </span>
                    </div>
                  </div>
                  <div v-else class="text-xs text-gray-500">
                    暂无健康检查数据
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-gray-200">
              <div class="flex space-x-4">
                <button 
                  @click="performHealthCheck(instance)"
                  :disabled="isLoading"
                  class="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  健康检查
                </button>
                <button 
                  @click="refreshInstanceStats(instance)"
                  :disabled="isLoading"
                  class="text-sm bg-green-500 text-white px-3 py-1 rounded hover:bg-green-600 disabled:opacity-50"
                >
                  刷新统计
                </button>
                <button 
                  @click="exportInstanceConfig(instance)"
                  class="text-sm bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600"
                >
                  导出配置
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑实例对话框 -->
    <TransitionRoot appear :show="showAddDialog || showEditDialog" as="template">
      <Dialog as="div" @close="closeDialog" class="relative z-10">
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
                  {{ showEditDialog ? '编辑Jenkins实例' : '添加Jenkins实例' }}
                </DialogTitle>

                <form @submit.prevent="saveInstance" class="mt-4 space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">实例名称 *</label>
                    <input 
                      type="text"
                      v-model="formData.name"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="如: 生产环境Jenkins"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Jenkins URL *</label>
                    <input 
                      type="url"
                      v-model="formData.url"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      placeholder="https://jenkins.example.com"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">用户名 *</label>
                    <input 
                      type="text"
                      v-model="formData.username"
                      required
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">API Token *</label>
                    <input 
                      type="password"
                      v-model="formData.token"
                      :required="!showEditDialog"
                      class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                      :placeholder="showEditDialog ? '留空保持不变' : 'Jenkins API Token'"
                    >
                    <p class="mt-1 text-xs text-gray-500">
                      在Jenkins中生成API Token: 用户设置 → API Token → 新增Token
                    </p>
                  </div>
                  
                  <div class="flex items-center">
                    <input 
                      type="checkbox"
                      v-model="formData.enabled"
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    >
                    <label class="ml-2 text-sm text-gray-900">启用此实例</label>
                  </div>
                  
                  <div class="flex items-center">
                    <input 
                      type="checkbox"
                      v-model="formData.autoHealthCheck"
                      class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    >
                    <label class="ml-2 text-sm text-gray-900">自动健康检查</label>
                  </div>

                  <div class="mt-6 flex justify-end space-x-3">
                    <button
                      type="button"
                      class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                      @click="closeDialog"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      :disabled="isLoading"
                      class="inline-flex justify-center rounded-md border border-transparent bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:opacity-50"
                    >
                      {{ isLoading ? '保存中...' : (showEditDialog ? '更新' : '保存') }}
                    </button>
                  </div>
                </form>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { fetchApi } from '@/utils/api'
import { notify } from '@/utils/notification'

// 响应式状态
const instances = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const isLoading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingInstance = ref(null)

// 表单数据
const formData = ref({
  name: '',
  url: '',
  username: '',
  token: '',
  enabled: true,
  autoHealthCheck: true
})

// 计算属性
const filteredInstances = computed(() => {
  return instances.value.filter(instance => {
    const matchesSearch = instance.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         instance.url.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = !statusFilter.value || 
                         (statusFilter.value === 'disabled' && !instance.enabled) ||
                         (statusFilter.value !== 'disabled' && instance.status === statusFilter.value)
    return matchesSearch && matchesStatus
  })
})

const onlineInstances = computed(() => 
  instances.value.filter(i => i.enabled && i.status === 'online')
)

const offlineInstances = computed(() => 
  instances.value.filter(i => i.enabled && i.status === 'offline')
)

const disabledInstances = computed(() => 
  instances.value.filter(i => !i.enabled)
)

// 方法
const getStatusClass = (status) => {
  switch (status) {
    case 'online': return 'bg-green-100 text-green-800'
    case 'offline': return 'bg-red-100 text-red-800'
    case 'testing': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'online': return '在线'
    case 'offline': return '离线'
    case 'testing': return '测试中'
    default: return '未知'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString()
}

const fetchInstances = async () => {
  isLoading.value = true
  try {
    const response = await fetchApi('/settings/jenkins', {
      method: 'GET'
    })
    
    if (response.success) {
      instances.value = response.data.map(instance => ({
        ...instance,
        status: instance.status || 'offline',
        showDetails: false
      }))
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('获取Jenkins实例失败:', error)
    notify.error(`获取实例列表失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const saveInstance = async () => {
  isLoading.value = true
  try {
    const url = showEditDialog.value 
      ? `/settings/jenkins/${editingInstance.value.id}`
      : '/settings/jenkins'
    
    const method = showEditDialog.value ? 'PUT' : 'POST'
    
    const response = await fetchApi(url, {
      method,
      body: formData.value
    })
    
    if (response.success) {
      notify.success(showEditDialog.value ? '实例更新成功' : '实例创建成功')
      closeDialog()
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存Jenkins实例失败:', error)
    notify.error(`保存失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const editInstance = (instance) => {
  editingInstance.value = instance
  formData.value = {
    name: instance.name,
    url: instance.url,
    username: instance.username,
    token: '', // 不显示原密码
    enabled: instance.enabled,
    autoHealthCheck: instance.autoHealthCheck || true
  }
  showEditDialog.value = true
}

const deleteInstance = async (instance) => {
  if (!(await notify.confirm(`确定要删除Jenkins实例 "${instance.name}" 吗？此操作不可恢复。`))) {
    return
  }
  
  try {
    const response = await fetchApi(`/settings/jenkins/${instance.id}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      notify.success('实例删除成功')
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('删除Jenkins实例失败:', error)
    notify.error(`删除失败: ${error.message}`)
  }
}

const toggleInstance = async (instance) => {
  const action = instance.enabled ? '禁用' : '启用'
  if (!(await notify.confirm(`确定要${action}实例 "${instance.name}" 吗？`))) {
    return
  }
  
  try {
    const response = await fetchApi(`/settings/jenkins/${instance.id}`, {
      method: 'PUT',
      body: {
        ...instance,
        enabled: !instance.enabled
      }
    })
    
    if (response.success) {
      notify.success(`实例${action}成功`)
      await fetchInstances()
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error(`${action}实例失败:`, error)
    notify.error(`${action}失败: ${error.message}`)
  }
}

const testConnection = async (instance) => {
  instance.status = 'testing'
  
  try {
    const response = await fetchApi(`/ops/jenkins/test/${instance.id}`, {
      method: 'POST'
    })
    
    if (response.success) {
      instance.status = 'online'
      instance.lastChecked = new Date().toLocaleString()
      instance.version = response.data.version
      instance.stats = response.data.stats
      notify.success(`连接测试成功: ${response.message}`)
    } else {
      instance.status = 'offline'
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('连接测试失败:', error)
    instance.status = 'offline'
    notify.error(`连接测试失败: ${error.message}`)
  }
}

const performHealthCheck = async (instance) => {
  try {
    const response = await fetchApi(`/ops/jenkins/health/${instance.id}`, {
      method: 'POST'
    })
    
    if (response.success) {
      instance.healthCheck = response.data
      notify.success('健康检查完成')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    notify.error(`健康检查失败: ${error.message}`)
  }
}

const refreshInstanceStats = async (instance) => {
  try {
    const response = await fetchApi(`/ops/jenkins/stats/${instance.id}`, {
      method: 'GET'
    })
    
    if (response.success) {
      instance.stats = response.data
      notify.success('统计信息已刷新')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('刷新统计失败:', error)
    notify.error(`刷新统计失败: ${error.message}`)
  }
}

const refreshAllInstances = async () => {
  isLoading.value = true
  try {
    // 并行测试所有启用的实例
    const enabledInstances = instances.value.filter(i => i.enabled)
    await Promise.allSettled(
      enabledInstances.map(instance => testConnection(instance))
    )
    notify.success('所有实例状态已刷新')
  } catch (error) {
    console.error('刷新实例状态失败:', error)
    notify.error('刷新实例状态失败')
  } finally {
    isLoading.value = false
  }
}

const viewInstanceDetails = (instance) => {
  instance.showDetails = !instance.showDetails
}

const exportInstanceConfig = (instance) => {
  const config = {
    name: instance.name,
    url: instance.url,
    username: instance.username,
    enabled: instance.enabled,
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `jenkins-instance-${instance.name}.json`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
  
  notify.success('配置导出成功')
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  editingInstance.value = null
  formData.value = {
    name: '',
    url: '',
    username: '',
    token: '',
    enabled: true,
    autoHealthCheck: true
  }
}

// 初始化
onMounted(async () => {
  await fetchInstances()
  
  // 监听全局刷新事件
  window.addEventListener('jenkins-refresh', fetchInstances)
})

onBeforeUnmount(() => {
  window.removeEventListener('jenkins-refresh', fetchInstances)
})
</script>

<style scoped>
/* 状态指示器动画 */
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

/* 过渡动画 */
.transition-colors {
  transition-property: background-color, border-color, color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* 响应式表格 */
@media (max-width: 768px) {
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