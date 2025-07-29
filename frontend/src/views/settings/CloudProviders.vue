<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">云厂商配置</h2>
      <button 
        @click="showCreateModal = true"
        class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 flex items-center gap-2"
      >
        <span>+</span>
        添加配置
      </button>
    </div>
    
    <!-- 配置列表 -->
    <div class="space-y-4">
      <div v-if="providers.length === 0" class="text-center py-8 text-gray-500">
        暂无云厂商配置，请点击右上角添加配置
      </div>
      
      <div 
        v-for="provider in providers" 
        :key="provider.id"
        class="border rounded-lg p-4 hover:bg-gray-50"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span class="text-2xl">{{ getProviderIcon(provider.provider) }}</span>
              <div>
                <h3 class="font-semibold text-lg">{{ provider.name }}</h3>
                <p class="text-sm text-gray-600">{{ getProviderLabel(provider.provider) }}</p>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500">区域:</span>
                <span class="ml-2">{{ provider.region || '未设置' }}</span>
              </div>
              <div>
                <span class="text-gray-500">状态:</span>
                <span class="ml-2">
                  <span v-if="provider.enabled" class="text-green-600">✓ 已启用</span>
                  <span v-else class="text-red-600">✗ 已禁用</span>
                </span>
              </div>
              <div>
                <span class="text-gray-500">创建时间:</span>
                <span class="ml-2">{{ formatDate(provider.created_at) }}</span>
              </div>
              <div>
                <span class="text-gray-500">更新时间:</span>
                <span class="ml-2">{{ formatDate(provider.updated_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <button 
              @click="testConnection(provider)"
              class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
              :disabled="testing === provider.id"
            >
              {{ testing === provider.id ? '测试中...' : '测试连接' }}
            </button>
            <button 
              @click="editProvider(provider)"
              class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
            >
              编辑
            </button>
            <button 
              @click="deleteProvider(provider)"
              class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
            >
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建/编辑模态框 -->
    <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4">
          {{ showCreateModal ? '添加云厂商配置' : '编辑云厂商配置' }}
        </h3>
        
        <form @submit.prevent="saveProvider" class="space-y-4">
          <!-- 配置名称 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">配置名称</label>
            <input 
              type="text" 
              v-model="currentProvider.name"
              placeholder="例如：生产环境阿里云"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
          </div>
          
          <!-- 云厂商类型 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">云厂商类型</label>
            <select 
              v-model="currentProvider.provider" 
              @change="onProviderChange"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">请选择云厂商</option>
              <option v-for="provider in supportedProviders" :key="provider.value" :value="provider.value">
                {{ provider.icon }} {{ provider.label }}
              </option>
            </select>
          </div>
          
          <!-- 动态配置字段 -->
          <div v-if="currentProvider.provider && providerSchemas[currentProvider.provider]">
            <h4 class="font-medium text-gray-700 mb-3">配置信息</h4>
            <div class="space-y-3">
              <div v-for="field in providerSchemas[currentProvider.provider]" :key="field.field_name">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  {{ field.field_label }}
                  <span v-if="field.is_required" class="text-red-500">*</span>
                </label>
                
                <!-- 文本输入框 -->
                <input 
                  v-if="field.field_type === 'text'"
                  type="text"
                  v-model="currentProvider.config[field.field_name]"
                  :placeholder="field.placeholder"
                  :required="field.is_required"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                
                <!-- 密码输入框 -->
                <input 
                  v-else-if="field.field_type === 'password'"
                  type="password"
                  v-model="currentProvider.config[field.field_name]"
                  :placeholder="field.placeholder"
                  :required="field.is_required"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                
                <!-- 下拉选择框 -->
                <select 
                  v-else-if="field.field_type === 'select'"
                  v-model="currentProvider.config[field.field_name]"
                  :required="field.is_required"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">请选择</option>
                  <option v-for="option in field.options" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                
                <!-- 文本域 -->
                <textarea 
                  v-else-if="field.field_type === 'textarea'"
                  v-model="currentProvider.config[field.field_name]"
                  :placeholder="field.placeholder"
                  :required="field.is_required"
                  rows="4"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                ></textarea>
                
                <!-- 帮助文本 -->
                <p v-if="field.help_text" class="text-xs text-gray-500 mt-1">
                  {{ field.help_text }}
                </p>
              </div>
            </div>
          </div>
          
          <!-- 是否启用 -->
          <div class="flex items-center">
            <input 
              type="checkbox" 
              v-model="currentProvider.enabled"
              id="enabled"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label for="enabled" class="ml-2 block text-sm text-gray-700">
              启用此配置
            </label>
          </div>
          
          <!-- 操作按钮 -->
          <div class="flex justify-end gap-3 pt-4">
            <button 
              type="button"
              @click="closeModal"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              取消
            </button>
            <button 
              type="submit"
              class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
              :disabled="saving"
            >
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchApi } from '@/utils/api'

// 数据状态
const providers = ref([])
const supportedProviders = ref([])
const providerSchemas = ref({})
const loading = ref(false)
const saving = ref(false)
const testing = ref(null)

// 模态框状态
const showCreateModal = ref(false)
const showEditModal = ref(false)
const currentProvider = ref({
  name: '',
  provider: '',
  config: {},
  region: '',
  enabled: true
})

// 获取云厂商配置列表
const fetchProviders = async () => {
  loading.value = true
  try {
    // 先尝试测试接口（无需认证）
    const response = await fetchApi('/cloud-providers-test')
    if (response.success) {
      providers.value = response.data
      return
    }
    
    // 如果测试接口失败，尝试正式接口
    const fallbackResponse = await fetchApi('/cloud-providers')
    if (fallbackResponse.success) {
      providers.value = fallbackResponse.data
    }
  } catch (error) {
    console.error('获取云厂商配置失败:', error)
    alert('获取云厂商配置失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取支持的云厂商列表
const fetchSupportedProviders = async () => {
  try {
    // 先尝试测试接口（无需认证）
    let response = await fetchApi('/cloud-providers/supported-test')
    if (response.success) {
      supportedProviders.value = response.data
      return
    }
    
    // 如果测试接口失败，尝试正式接口
    response = await fetchApi('/cloud-providers/supported')
    if (response.success) {
      supportedProviders.value = response.data
    }
  } catch (error) {
    console.error('获取支持的云厂商列表失败:', error)
  }
}

// 获取云厂商配置字段定义
const fetchProviderSchemas = async () => {
  try {
    // 先尝试测试接口（无需认证）
    let response = await fetchApi('/cloud-providers/schemas-test')
    if (response.success) {
      providerSchemas.value = response.data
      return
    }
    
    // 如果测试接口失败，尝试正式接口
    response = await fetchApi('/cloud-providers/schemas')
    if (response.success) {
      providerSchemas.value = response.data
    }
  } catch (error) {
    console.error('获取云厂商配置字段定义失败:', error)
  }
}

// 获取云厂商图标
const getProviderIcon = (provider) => {
  const icons = {
    'aliyun': '🌐',
    'aws': '☁️',
    'tencent': '🐧',
    'huawei': '🌸',
    'google': '🔍',
    'azure': '🪟'
  }
  return icons[provider] || '☁️'
}

// 获取云厂商标签
const getProviderLabel = (provider) => {
  const labels = {
    'aliyun': '阿里云',
    'aws': 'Amazon Web Services',
    'tencent': '腾讯云',
    'huawei': '华为云',
    'google': 'Google Cloud',
    'azure': 'Microsoft Azure'
  }
  return labels[provider] || provider
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 云厂商类型改变处理
const onProviderChange = () => {
  // 重置配置
  currentProvider.value.config = {}
  
  // 设置默认值
  if (currentProvider.value.provider && providerSchemas.value[currentProvider.value.provider]) {
    const schema = providerSchemas.value[currentProvider.value.provider]
    schema.forEach(field => {
      if (field.default_value) {
        currentProvider.value.config[field.field_name] = field.default_value
      }
    })
  }
}

// 编辑云厂商配置
const editProvider = (provider) => {
  currentProvider.value = {
    ...provider,
    config: { ...provider.config }
  }
  showEditModal.value = true
}

// 保存云厂商配置
const saveProvider = async () => {
  saving.value = true
  try {
    const isEdit = showEditModal.value
    const url = isEdit ? `/cloud-providers/${currentProvider.value.id}` : '/cloud-providers'
    const method = isEdit ? 'PUT' : 'POST'
    
    const response = await fetchApi(url, {
      method,
      body: currentProvider.value
    })
    
    if (response.success) {
      alert(isEdit ? '配置更新成功' : '配置创建成功')
      closeModal()
      fetchProviders()
    } else {
      throw new Error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存云厂商配置失败:', error)
    alert(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 删除云厂商配置
const deleteProvider = async (provider) => {
  if (!confirm(`确定要删除配置"${provider.name}"吗？`)) {
    return
  }
  
  try {
    const response = await fetchApi(`/cloud-providers/${provider.id}`, {
      method: 'DELETE'
    })
    
    if (response.success) {
      alert('配置删除成功')
      fetchProviders()
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error) {
    console.error('删除云厂商配置失败:', error)
    alert(error.message || '删除失败')
  }
}

// 测试连接
const testConnection = async (provider) => {
  testing.value = provider.id
  try {
    const response = await fetchApi(`/cloud-providers/${provider.id}/test`, {
      method: 'POST'
    })
    
    if (response.success) {
      alert(`✓ ${response.message}`)
    } else {
      throw new Error(response.message || '测试失败')
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    alert(`✗ ${error.message || '测试失败'}`)
  } finally {
    testing.value = null
  }
}

// 关闭模态框
const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  currentProvider.value = {
    name: '',
    provider: '',
    config: {},
    region: '',
    enabled: true
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    fetchProviders(),
    fetchSupportedProviders(),
    fetchProviderSchemas()
  ])
})
</script>