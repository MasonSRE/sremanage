<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <div v-for="(stat, index) in stats" :key="index" class="bg-white p-4 rounded-lg shadow">
      <h3 class="text-sm text-gray-500">{{ stat.label }}</h3>
      <div class="flex items-center mt-2">
        <span class="text-2xl font-bold">{{ stat.value }}</span>
        <span :class="[
          'ml-2 text-sm',
          stat.change.startsWith('+') ? 'text-green-500' : 'text-red-500'
        ]">
          {{ stat.change }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stats: {
    type: Array,
    required: true
  }
})
</script>