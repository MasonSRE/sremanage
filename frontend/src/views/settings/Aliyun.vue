<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold mb-6">阿里云账号</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700">Access Key ID</label>
        <input 
          type="text" 
          v-model="settings.accessKeyId"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Access Key Secret</label>
        <input 
          type="password" 
          v-model="settings.accessKeySecret"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
      </div>


      <div class="flex justify-end">
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
  accessKeyId: '',
  accessKeySecret: ''
})

const fetchSettings = async () => {
  try {
    const response = await fetchApi('/settings/aliyun', {
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
    const response = await fetchApi('/settings/aliyun', {
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

onMounted(fetchSettings)
</script> 