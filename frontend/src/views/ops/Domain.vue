<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">域名管理</h2>
      <div v-if="!hasAliyunConfig" class="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md">
        需要添加阿里云账号相关配置
      </div>
    </div>

    <!-- 配置检查提示 -->
    <div v-if="!hasAliyunConfig" class="mb-6 p-4 bg-orange-50 border border-orange-200 rounded-md">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-orange-400 mt-0.5 mr-3" />
        <div>
          <h3 class="text-sm font-medium text-orange-800">需要配置阿里云账号</h3>
          <div class="mt-1 text-sm text-orange-700">
            <p>请先在系统设置中配置阿里云Access Key ID和Secret才能使用域名管理功能。</p>
            <router-link 
              to="/settings/aliyun" 
              class="mt-2 inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-orange-700 bg-orange-100 hover:bg-orange-200"
            >
              前往配置
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 域名管理主要内容 -->
    <div v-if="hasAliyunConfig">
      <!-- 操作栏 -->
      <div class="mb-6 flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <button
            @click="fetchDomains"
            :disabled="loadingDomains"
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loadingDomains">加载中...</span>
            <span v-else>刷新域名列表</span>
          </button>
          <div v-if="lastSyncTime" class="text-sm text-gray-500">
            最后同步: {{ lastSyncTime }}
          </div>
        </div>
        
        <div class="text-sm text-gray-600">
          共 {{ domains.length }} 个域名
        </div>
      </div>

      <!-- 域名列表 -->
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">域名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">域名类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">是否为高级域名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">注册时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">到期时间</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="domain in domains" :key="domain.domain_name">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <GlobeAltIcon class="h-4 w-4 text-blue-500 mr-2" />
                  <span class="font-medium text-gray-900">{{ domain.domain_name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  getDomainStatusColor(domain.domain_status)
                ]">
                  {{ getDomainStatusText(domain.domain_status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ domain.domain_type || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  domain.premium ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                ]">
                  {{ domain.premium ? '高级域名' : '普通域名' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(domain.registration_date) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <span :class="getExpirationColor(domain.expiration_date)">
                  {{ formatDate(domain.expiration_date) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button 
                  @click="showDomainDetails(domain)"
                  class="text-blue-600 hover:text-blue-900 mr-2"
                >
                  详情
                </button>
                <button 
                  v-if="domain.domain_status === 'REGISTRAR_HOLD'"
                  class="text-orange-600 hover:text-orange-900"
                >
                  续费
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <div v-if="!loadingDomains && domains.length === 0" class="text-center py-12">
        <GlobeAltIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无域名</h3>
        <p class="mt-1 text-sm text-gray-500">您还没有在阿里云注册任何域名</p>
      </div>
    </div>

    <!-- 域名详情对话框 -->
    <TransitionRoot appear :show="showDetailDialog" as="template">
      <Dialog as="div" @close="showDetailDialog = false" class="relative z-10">
        <TransitionChild
          as="template"
          enter="duration-300 ease-out"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="duration-200 ease-in"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-black bg-opacity-25" />
        </TransitionChild>

        <div class="fixed inset-0 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="template"
              enter="duration-300 ease-out"
              enter-from="opacity-0 scale-95"
              enter-to="opacity-100 scale-100"
              leave="duration-200 ease-in"
              leave-from="opacity-100 scale-100"
              leave-to="opacity-0 scale-95"
            >
              <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 mb-4">
                  域名详情
                </DialogTitle>

                <div v-if="selectedDomain" class="space-y-4">
                  <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-3">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">域名</label>
                        <p class="mt-1 text-sm text-gray-900">{{ selectedDomain.domain_name }}</p>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">状态</label>
                        <span :class="[
                          'mt-1 px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                          getDomainStatusColor(selectedDomain.domain_status)
                        ]">
                          {{ getDomainStatusText(selectedDomain.domain_status) }}
                        </span>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">域名类型</label>
                        <p class="mt-1 text-sm text-gray-900">{{ selectedDomain.domain_type || '-' }}</p>
                      </div>
                    </div>
                    <div class="space-y-3">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">产品ID</label>
                        <p class="mt-1 text-sm text-gray-900">{{ selectedDomain.product_id || '-' }}</p>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">是否为高级域名</label>
                        <span :class="[
                          'mt-1 px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                          selectedDomain.premium ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                        ]">
                          {{ selectedDomain.premium ? '高级域名' : '普通域名' }}
                        </span>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">注册时间</label>
                        <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedDomain.registration_date) }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700">到期时间</label>
                    <p :class="['mt-1 text-sm', getExpirationColor(selectedDomain.expiration_date)]">
                      {{ formatDate(selectedDomain.expiration_date) }}
                      {{ getExpirationWarning(selectedDomain.expiration_date) }}
                    </p>
                  </div>
                </div>

                <div class="mt-6 flex justify-end">
                  <button
                    type="button"
                    @click="showDetailDialog = false"
                    class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    关闭
                  </button>
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
import { ref, onMounted } from 'vue'
import { 
  ExclamationTriangleIcon, 
  GlobeAltIcon 
} from '@heroicons/vue/24/outline'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { fetchApi } from '../../utils/api'

const hasAliyunConfig = ref(false)
const loadingDomains = ref(false)
const domains = ref([])
const lastSyncTime = ref('')
const showDetailDialog = ref(false)
const selectedDomain = ref(null)

// 检查阿里云配置
const checkAliyunConfig = async () => {
  try {
    const response = await fetchApi('/settings/aliyun')
    if (response.success && response.data.accessKeyId && response.data.accessKeyId.trim() !== '') {
      hasAliyunConfig.value = true
      return true
    }
    hasAliyunConfig.value = false
    return false
  } catch (error) {
    console.error('检查阿里云配置失败:', error)
    hasAliyunConfig.value = false
    return false
  }
}

// 获取域名列表
const fetchDomains = async () => {
  if (!hasAliyunConfig.value) return

  loadingDomains.value = true
  try {
    const response = await fetchApi('/aliyun/domains')
    if (response.success) {
      domains.value = response.data || []
      lastSyncTime.value = new Date().toLocaleString()
    } else {
      throw new Error(response.message || '获取域名列表失败')
    }
  } catch (error) {
    console.error('获取域名列表失败:', error)
    alert('获取域名列表失败: ' + error.message)
  } finally {
    loadingDomains.value = false
  }
}

// 显示域名详情
const showDomainDetails = (domain) => {
  selectedDomain.value = domain
  showDetailDialog.value = true
}

// 域名状态文本转换
const getDomainStatusText = (status) => {
  const statusMap = {
    'REGISTRAR_HOLD': '注册商暂停',
    'REGISTRY_HOLD': '注册局暂停', 
    'CLIENT_HOLD': '客户端暂停',
    'PENDING_DELETE': '等待删除',
    'PENDING_TRANSFER': '等待转移',
    'ACTIVE': '正常',
    'INACTIVE': '非活跃',
    'EXPIRED': '已过期'
  }
  return statusMap[status] || status
}

// 域名状态颜色
const getDomainStatusColor = (status) => {
  const colorMap = {
    'ACTIVE': 'bg-green-100 text-green-800',
    'REGISTRAR_HOLD': 'bg-yellow-100 text-yellow-800',
    'REGISTRY_HOLD': 'bg-yellow-100 text-yellow-800',
    'CLIENT_HOLD': 'bg-yellow-100 text-yellow-800',
    'PENDING_DELETE': 'bg-red-100 text-red-800',
    'PENDING_TRANSFER': 'bg-blue-100 text-blue-800',
    'EXPIRED': 'bg-red-100 text-red-800',
    'INACTIVE': 'bg-gray-100 text-gray-800'
  }
  return colorMap[status] || 'bg-gray-100 text-gray-800'
}

// 到期时间颜色
const getExpirationColor = (expirationDate) => {
  if (!expirationDate) return 'text-gray-500'
  
  const expiration = new Date(expirationDate)
  const now = new Date()
  const daysUntilExpiration = Math.ceil((expiration - now) / (1000 * 60 * 60 * 24))
  
  if (daysUntilExpiration < 0) {
    return 'text-red-600 font-medium' // 已过期
  } else if (daysUntilExpiration <= 30) {
    return 'text-orange-600 font-medium' // 30天内到期
  } else if (daysUntilExpiration <= 90) {
    return 'text-yellow-600' // 90天内到期
  }
  return 'text-gray-500'
}

// 到期警告文本
const getExpirationWarning = (expirationDate) => {
  if (!expirationDate) return ''
  
  const expiration = new Date(expirationDate)
  const now = new Date()
  const daysUntilExpiration = Math.ceil((expiration - now) / (1000 * 60 * 60 * 24))
  
  if (daysUntilExpiration < 0) {
    return `（已过期 ${Math.abs(daysUntilExpiration)} 天）`
  } else if (daysUntilExpiration <= 30) {
    return `（${daysUntilExpiration} 天后到期）`
  }
  return ''
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleDateString()
  } catch {
    return dateString
  }
}

onMounted(async () => {
  await checkAliyunConfig()
  if (hasAliyunConfig.value) {
    fetchDomains()
  }
})
</script>