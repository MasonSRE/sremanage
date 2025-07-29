<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">CDN管理</h2>
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
            <p>请先在系统设置中配置阿里云Access Key ID和Secret才能使用CDN管理功能。</p>
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

    <!-- CDN域名列表 -->
    <div v-if="hasAliyunConfig" class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-medium text-gray-900">CDN域名列表</h3>
        <button
          @click="fetchCdnDomains"
          :disabled="loadingDomains"
          class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loadingDomains">加载中...</span>
          <span v-else>刷新域名列表</span>
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">域名</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CDN类型</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SSL协议</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="domain in cdnDomains" :key="domain.domain_name">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="w-2 h-2 mr-2 bg-blue-500 rounded-full"></span>
                  {{ domain.domain_name }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  domain.domain_status === 'online' ? 'bg-green-100 text-green-800' : 
                  domain.domain_status === 'offline' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                ]">
                  {{ getDomainStatusText(domain.domain_status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ domain.cdn_type }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ domain.ssl_protocol || '-' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(domain.gmt_created) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loadingDomains && cdnDomains.length === 0" class="text-center py-8">
        <CloudIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">暂无CDN域名</h3>
        <p class="mt-1 text-sm text-gray-500">您还没有配置任何CDN域名</p>
      </div>
    </div>

    <!-- CDN操作区域 -->
    <div v-if="hasAliyunConfig" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- CDN刷新 -->
      <div class="bg-gray-50 rounded-lg p-6">
        <div class="flex items-center mb-4">
          <ArrowPathIcon class="h-6 w-6 text-blue-500 mr-2" />
          <h3 class="text-lg font-medium text-gray-900">CDN缓存刷新</h3>
        </div>
        <p class="text-sm text-gray-600 mb-4">
          删除CDN边缘节点上的指定缓存内容，下次访问时将回源获取最新内容
        </p>
        
        <form @submit.prevent="handleRefresh">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">刷新URL（每行一个）</label>
            <textarea 
              v-model="refreshUrls"
              rows="6"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="https://example.com/path/file.js&#10;https://example.com/images/image.png"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">支持文件刷新和目录刷新，最多100个URL</p>
          </div>
          
          <button 
            type="submit"
            :disabled="!refreshUrls.trim() || refreshLoading"
            class="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="refreshLoading">刷新中...</span>
            <span v-else>开始刷新</span>
          </button>
        </form>
      </div>

      <!-- CDN预热 -->
      <div class="bg-gray-50 rounded-lg p-6">
        <div class="flex items-center mb-4">
          <FireIcon class="h-6 w-6 text-orange-500 mr-2" />
          <h3 class="text-lg font-medium text-gray-900">CDN缓存预热</h3>
        </div>
        <p class="text-sm text-gray-600 mb-4">
          主动将指定内容预加载到CDN边缘节点，提高首次访问速度
        </p>
        
        <form @submit.prevent="handlePreload">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">预热URL（每行一个）</label>
            <textarea 
              v-model="preloadUrls"
              rows="6"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
              placeholder="https://example.com/path/file.js&#10;https://example.com/images/image.png"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">仅支持文件预热，最多50个URL</p>
          </div>
          
          <button 
            type="submit"
            :disabled="!preloadUrls.trim() || preloadLoading"
            class="w-full bg-orange-500 text-white px-4 py-2 rounded-md hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="preloadLoading">预热中...</span>
            <span v-else>开始预热</span>
          </button>
        </form>
      </div>
    </div>

    <!-- 操作历史 -->
    <div v-if="hasAliyunConfig && operationHistory.length > 0" class="mt-8">
      <h3 class="text-lg font-medium text-gray-900 mb-4">操作历史</h3>
      <div class="bg-gray-50 rounded-lg p-4">
        <div class="space-y-3">
          <div v-for="(operation, index) in operationHistory" :key="index" class="flex items-start space-x-3">
            <div class="flex-shrink-0">
              <div :class="[
                'w-2 h-2 rounded-full mt-2',
                operation.type === 'refresh' ? 'bg-blue-500' : 'bg-orange-500'
              ]"></div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-900">
                <span class="font-medium">{{ operation.type === 'refresh' ? 'CDN刷新' : 'CDN预热' }}</span>
                {{ operation.success ? '成功' : '失败' }}
              </p>
              <p class="text-xs text-gray-500">
                {{ operation.time }} | 任务ID: {{ operation.taskId }}
              </p>
              <p v-if="operation.urls" class="text-xs text-gray-600 mt-1">
                处理了 {{ operation.urls.length }} 个URL
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  ExclamationTriangleIcon, 
  ArrowPathIcon, 
  FireIcon, 
  CloudIcon 
} from '@heroicons/vue/24/outline'
import { fetchApi } from '../../utils/api'

const hasAliyunConfig = ref(false)
const loadingDomains = ref(false)
const refreshLoading = ref(false)
const preloadLoading = ref(false)

const cdnDomains = ref([])
const refreshUrls = ref('')
const preloadUrls = ref('')
const operationHistory = ref([])

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

// 获取CDN域名列表
const fetchCdnDomains = async () => {
  if (!hasAliyunConfig.value) return

  loadingDomains.value = true
  try {
    const response = await fetchApi('/aliyun/cdn/domains')
    if (response.success) {
      cdnDomains.value = response.data || []
    } else {
      throw new Error(response.message || '获取CDN域名列表失败')
    }
  } catch (error) {
    console.error('获取CDN域名列表失败:', error)
    alert('获取CDN域名列表失败: ' + error.message)
  } finally {
    loadingDomains.value = false
  }
}

// CDN缓存刷新
const handleRefresh = async () => {
  if (!refreshUrls.value.trim()) return

  const urls = refreshUrls.value.split('\n').filter(url => url.trim()).map(url => url.trim())
  
  if (urls.length === 0) {
    alert('请输入要刷新的URL')
    return
  }

  if (urls.length > 100) {
    alert('最多支持100个URL')
    return
  }

  refreshLoading.value = true
  try {
    const response = await fetchApi('/aliyun/cdn/refresh', {
      method: 'POST',
      body: { urls }
    })

    if (response.success) {
      alert('CDN缓存刷新任务提交成功')
      
      // 添加到操作历史
      operationHistory.value.unshift({
        type: 'refresh',
        success: true,
        time: new Date().toLocaleString(),
        taskId: response.task_id,
        urls: urls
      })
      
      refreshUrls.value = ''
    } else {
      throw new Error(response.message || 'CDN缓存刷新失败')
    }
  } catch (error) {
    console.error('CDN缓存刷新失败:', error)
    alert('CDN缓存刷新失败: ' + error.message)
    
    // 添加失败记录到操作历史
    operationHistory.value.unshift({
      type: 'refresh',
      success: false,
      time: new Date().toLocaleString(),
      taskId: '-',
      urls: urls
    })
  } finally {
    refreshLoading.value = false
  }
}

// CDN缓存预热
const handlePreload = async () => {
  if (!preloadUrls.value.trim()) return

  const urls = preloadUrls.value.split('\n').filter(url => url.trim()).map(url => url.trim())
  
  if (urls.length === 0) {
    alert('请输入要预热的URL')
    return
  }

  if (urls.length > 50) {
    alert('最多支持50个URL')
    return
  }

  preloadLoading.value = true
  try {
    const response = await fetchApi('/aliyun/cdn/preload', {
      method: 'POST',
      body: { urls }
    })

    if (response.success) {
      alert('CDN缓存预热任务提交成功')
      
      // 添加到操作历史
      operationHistory.value.unshift({
        type: 'preload',
        success: true,
        time: new Date().toLocaleString(),
        taskId: response.task_id,
        urls: urls
      })
      
      preloadUrls.value = ''
    } else {
      throw new Error(response.message || 'CDN缓存预热失败')
    }
  } catch (error) {
    console.error('CDN缓存预热失败:', error)
    alert('CDN缓存预热失败: ' + error.message)
    
    // 添加失败记录到操作历史
    operationHistory.value.unshift({
      type: 'preload',
      success: false,
      time: new Date().toLocaleString(),
      taskId: '-',
      urls: urls
    })
  } finally {
    preloadLoading.value = false
  }
}

// 域名状态文本转换
const getDomainStatusText = (status) => {
  const statusMap = {
    'online': '在线',
    'offline': '离线',
    'configuring': '配置中',
    'configure_failed': '配置失败',
    'checking': '审核中',
    'check_failed': '审核失败'
  }
  return statusMap[status] || status
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(async () => {
  await checkAliyunConfig()
  if (hasAliyunConfig.value) {
    fetchCdnDomains()
  }
})
</script>