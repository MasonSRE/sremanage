<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold mb-6">邮箱配置</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700">SMTP 服务器</label>
        <input 
          type="text" 
          v-model="settings.smtpServer"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="例如: smtp.example.com"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">SMTP 端口</label>
        <input 
          type="number" 
          v-model="settings.smtpPort"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="例如: 587"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">发件人邮箱</label>
        <input 
          type="email" 
          v-model="settings.senderEmail"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="例如: sender@example.com"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">邮箱密码</label>
        <input 
          type="password" 
          v-model="settings.password"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>

      <div class="flex items-center space-x-2">
        <input 
          type="checkbox" 
          v-model="settings.useTLS"
          class="rounded text-blue-600"
          id="use-tls"
        >
        <label for="use-tls" class="text-sm text-gray-700">使用 TLS 加密</label>
      </div>

      <div class="flex justify-end space-x-4">
        <button 
          type="button"
          @click="testConnection"
          class="bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200"
        >
          测试连接
        </button>
        <button 
          type="submit"
          class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
        >
          保存设置
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchApi } from '@/utils/api'

const settings = ref({
  smtpServer: '',
  smtpPort: 587,
  senderEmail: '',
  password: '',
  useTLS: true
})

const fetchSettings = async () => {
  try {
    const response = await fetchApi('/settings/mail', {
      method: 'GET'
    })
    if (response.success) {
      settings.value = response.data
    }
  } catch (error) {
    console.error('获取设置失败:', error)
  }
}

const saveSettings = async () => {
  try {
    const response = await fetchApi('/settings/mail', {
      method: 'POST',
      body: settings.value
    })
    if (response.success) {
      alert('保存成功')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('保存设置失败:', error)
    alert(error.message || '保存失败')
  }
}

const testConnection = async () => {
  try {
    const response = await fetchApi('/settings/mail/test', {
      method: 'POST',
      body: settings.value
    })
    if (response.success) {
      alert('连接测试成功')
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('测试连接失败:', error)
    alert(error.message || '测试失败')
  }
}

onMounted(fetchSettings)
</script> 