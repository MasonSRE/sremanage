<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold text-green-600">✅ 测试页面正常工作</h1>
    <p class="mt-4 text-gray-600">如果你能看到这个页面，说明Vue和路由基本功能正常</p>
    <div class="mt-4 p-4 bg-blue-50 rounded">
      <p class="text-blue-800">当前时间: {{ currentTime }}</p>
      <p class="text-blue-800">测试数据: {{ testData }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentTime = ref('')
const testData = ref('Vue响应式数据正常')

onMounted(() => {
  currentTime.value = new Date().toLocaleString()
  console.log('SimpleTest组件已挂载')
})
</script>