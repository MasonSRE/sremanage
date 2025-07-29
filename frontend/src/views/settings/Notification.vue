<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold mb-6">告警设置</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- 启用告警开关 -->
      <div class="flex items-center justify-between">
        <span class="text-gray-700">启用告警通知</span>
        <Switch
          v-model="settings.enabled"
          class="relative inline-flex h-6 w-11 items-center rounded-full"
          :class="settings.enabled ? 'bg-blue-600' : 'bg-gray-200'"
        >
          <span class="sr-only">启用告警通知</span>
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white transition"
            :class="settings.enabled ? 'translate-x-6' : 'translate-x-1'"
          />
        </Switch>
      </div>

      <!-- 通知方式 -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">通知方式</label>
        <div class="space-x-4">
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              v-model="settings.methods.email"
              class="rounded text-blue-600"
            />
            <span class="ml-2">邮件通知</span>
          </label>
          
          <!-- 短信通知选项 - 禁用状态 -->
          <label class="inline-flex items-center opacity-50 cursor-not-allowed">
            <input
              type="checkbox"
              disabled
              class="rounded text-gray-400 cursor-not-allowed"
            />
            <span class="ml-2">短信通知</span>
          </label>
        </div>
      </div>

      <!-- 告警级别 -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-gray-700">告警级别</label>
        <div class="space-y-2">
          <label class="inline-flex items-center">
            <input
              type="checkbox"
              v-model="settings.levels.error"
              class="rounded text-blue-600"
            />
            <span class="ml-2">错误</span>
          </label>
          <label class="inline-flex items-center ml-4">
            <input
              type="checkbox"
              v-model="settings.levels.warning"
              class="rounded text-blue-600"
            />
            <span class="ml-2">警告</span>
          </label>
          <label class="inline-flex items-center ml-4">
            <input
              type="checkbox"
              v-model="settings.levels.info"
              class="rounded text-blue-600"
            />
            <span class="ml-2">信息</span>
          </label>
        </div>
      </div>

      <!-- 保存按钮 -->
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
import { ref } from 'vue'
import { Switch } from '@headlessui/vue'
import { fetchApi } from '@/utils/api'

const settings = ref({
  enabled: true,
  methods: {
    email: true,
    sms: false  // 短信通知默认禁用
  },
  levels: {
    error: true,
    warning: true,
    info: false
  }
})

// 获取设置
const fetchSettings = async () => {
  try {
    const response = await fetchApi('/settings/notification', {
      method: 'GET'
    })
    if (response.success) {
      settings.value = response.data
    }
  } catch (error) {
    console.error('获取设置失败:', error)
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    const response = await fetchApi('/settings/notification', {
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

// 页面加载时获取设置
fetchSettings()
</script> 