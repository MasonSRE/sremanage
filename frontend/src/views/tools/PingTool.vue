<template>
  <div class="bg-white rounded-lg shadow">
    <div class="p-6 border-b border-gray-200">
      <h2 class="text-xl font-semibold">多地Ping工具</h2>
    </div>
    <div class="relative w-full h-[800px]">
      <iframe
        :src="pingToolUrl"
        class="absolute inset-0 w-full h-full"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const pingToolUrl = ref('https://globalping.io/network-tools/ping-from-world') // 替换为实际的URL
</script>

<script>
export default {
  name: 'PingTool'
}
</script>

<style scoped>
/* 可以根据需要添加自定义样式 */
iframe {
  border: none;
}
</style> 