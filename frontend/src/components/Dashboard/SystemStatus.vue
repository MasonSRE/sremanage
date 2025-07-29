<template>
  <div class="bg-white p-6 rounded-lg shadow">
    <h2 class="text-lg font-semibold mb-4">系统服务状态</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="(service, index) in services" :key="index" 
           class="border p-4 rounded-lg">
        <div class="flex items-center justify-between">
          <span>{{ service.name }}</span>
          <span class="flex items-center">
            <span :class="[
              'w-2 h-2 rounded-full mr-2',
              service.statusColor
            ]"></span>
            {{ service.status }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  services: {
    type: Array,
    required: true
  }
})
</script>