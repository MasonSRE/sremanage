<template>
  <div class="bg-white rounded-lg shadow p-6">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-semibold">更新管理</h2>
      <button 
        @click="checkUpdates"
        class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
      >
        检查更新
      </button>
    </div>

    <!-- 更新列表 -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead>
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">主机</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">软件包</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">当前版本</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最新版本</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="update in updates" :key="update.id">
            <td class="px-6 py-4 whitespace-nowrap">{{ update.hostname }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ update.package_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ update.current_version }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ update.latest_version }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(update.status)">
                {{ getStatusText(update.status) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <button 
                @click="handleUpdate(update)"
                :disabled="!canUpdate(update)"
                class="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                更新
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 更新日志 -->
    <div v-if="updateLogs.length" class="mt-6">
      <h3 class="text-lg font-medium mb-2">更新日志</h3>
      <div class="bg-gray-50 rounded-md p-4 h-64 overflow-y-auto font-mono text-sm">
        <div v-for="(log, index) in updateLogs" :key="index" class="mb-1">
          {{ log }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { fetchApi } from '@/utils/api'

const updates = ref([])
const updateLogs = ref([])

// 检查更新
const checkUpdates = async () => {
  try {
    const response = await fetchApi('/software/check-updates')
    if (response.success) {
      updates.value = response.data
    }
  } catch (error) {
    console.error('检查更新失败:', error)
  }
}

// 处理更新
const handleUpdate = async (update) => {
  try {
    updateLogs.value.push(`开始更新 ${update.hostname} 上的 ${update.package_name}...`)
    
    const response = await fetchApi('/software/update', {
      method: 'POST',
      body: {
        host_id: update.host_id,
        package_id: update.package_id
      }
    })

    if (response.success) {
      updateLogs.value.push('更新成功!')
      checkUpdates() // 刷新更新列表
    } else {
      updateLogs.value.push(`更新失败: ${response.message}`)
    }
  } catch (error) {
    console.error('更新失败:', error)
    updateLogs.value.push(`更新出错: ${error.message}`)
  }
}

// 获取状态样式
const getStatusClass = (status) => {
  const classes = {
    available: 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800',
    updating: 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800',
    error: 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800',
    uptodate: 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800'
  }
  return classes[status] || classes.error
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    available: '可更新',
    updating: '更新中',
    error: '错误',
    uptodate: '已是最新'
  }
  return texts[status] || '未知'
}

// 检查是否可以更新
const canUpdate = (update) => {
  return update.status === 'available'
}
</script> 