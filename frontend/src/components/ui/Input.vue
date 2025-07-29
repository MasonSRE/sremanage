<template>
    <div>
      <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
        {{ label }}
      </label>
      <input
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :class="[
          'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
          error ? 'border-red-300' : 'border-gray-300'
        ]"
        v-bind="$attrs"
      >
      <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    </div>
  </template>
  
  <script setup>
  defineProps({
    label: String,
    modelValue: [String, Number],
    type: {
      type: String,
      default: 'text'
    },
    error: String
  })
  
  defineEmits(['update:modelValue'])
  </script>